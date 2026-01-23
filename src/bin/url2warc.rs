use std::io::SeekFrom;
use std::io::Write;
use std::os::unix::fs::MetadataExt;
use std::time::Duration;

use anyhow::Result;
use chrono::{SecondsFormat, Utc};
use itertools::Itertools;
use reqwest::Response;
use tokio::io::AsyncWriteExt;
use tokio::io::BufWriter;
use tokio::io::{AsyncReadExt, AsyncSeekExt, BufReader};
use tokio::sync::mpsc;
use tokio::{fs::File, io::AsyncBufReadExt};
use tqdm::Tqdm;
use uuid::Uuid;

#[tokio::main]
async fn main() -> Result<()> {
    let root_dir = env!("CARGO_MANIFEST_DIR");
    let enwiki_urls_txt = format!("{root_dir}/assets/datasets/quality_identifier/enwiki-urls.txt");
    let output_warc = format!("{root_dir}/assets/warcs/subsampled_positive_urls.warc");
    if !std::fs::exists(&enwiki_urls_txt)? {
        panic!("{enwiki_urls_txt} doesn't exist");
    }
    if std::fs::exists(&output_warc)? {
        panic!("{output_warc} already exists");
    }

    let mut urls_file = BufReader::new(File::open(&enwiki_urls_txt).await?);
    let n_chunks = 8;
    let chunks = chunk_urls(&mut urls_file, n_chunks).await?;

    let mut buf = [0u8; 8 * 1024];
    let mut linebreaks_count = 0;
    loop {
        let n = urls_file.read(&mut buf).await?;
        if n == 0 {
            break;
        }
        linebreaks_count += buf[..n].iter().filter(|&&b| b == b'\n').count();
    }

    let (tx, rx) = mpsc::channel::<Vec<u8>>(n_chunks);

    for (&s, &e) in chunks.iter().tuple_windows() {
        let urls_file = BufReader::new(File::open(&enwiki_urls_txt).await?);
        tokio::spawn(fetch_urls(urls_file, s, e, tx.clone()));
    }

    drop(tx);

    let pb = tqdm::pbar(Some(linebreaks_count));
    let writer = BufWriter::new(File::create(output_warc).await?);
    reduce_warc(writer, rx, Some(pb)).await?;

    Ok(())
}

async fn chunk_urls(f: &mut BufReader<File>, n: usize) -> Result<Vec<u64>> {
    let file_size = f.get_ref().metadata().await?.size();
    let chunk_size = file_size as usize / n;
    let mut splits = Vec::with_capacity(n);
    splits.push(0);

    for i in 1..n {
        let start = i * chunk_size;
        f.seek(SeekFrom::Start(start as u64)).await?;
        while f.read_u8().await? != b'\n' {}
        splits.push(f.stream_position().await?);
    }

    splits.push(file_size);
    splits.sort_unstable();
    splits.dedup();

    Ok(splits)
}

async fn fetch_urls(
    mut f: BufReader<File>,
    start: u64,
    end: u64,
    tx: mpsc::Sender<Vec<u8>>,
) -> Result<()> {
    f.seek(SeekFrom::Start(start)).await?;

    let client = reqwest::Client::builder()
        .timeout(Duration::from_secs(3))
        .build()?;
    let mut buf = Vec::with_capacity(4096);
    let mut has_read_bytes = 0;

    while has_read_bytes + start < end {
        buf.clear();

        let n = f.read_until(b'\n', &mut buf).await?;
        if n == 0 {
            break;
        }

        has_read_bytes += n as u64;

        let url = String::from_utf8_lossy(&buf);
        let url = url.trim();

        if url.is_empty() {
            continue;
        }

        let resp = match client.get(url).send().await {
            Ok(r) => r,
            Err(_) => continue,
        };

        let warc_bytes = match http_resp_to_warc(resp, url).await {
            Ok(b) => b,
            _ => continue,
        };
        tx.send(warc_bytes).await?;
    }

    Ok(())
}

async fn http_resp_to_warc(resp: Response, target_uri: &str) -> Result<Vec<u8>> {
    let status = resp.status();
    let reason = status
        .canonical_reason()
        .ok_or_else(|| anyhow::format_err!("no canonical reason for status {}", status))?;

    let mut http_bytes = Vec::new();

    // status line
    write!(
        &mut http_bytes,
        "HTTP/1.1 {} {}\r\n",
        status.as_u16(),
        reason
    )?;

    // headers
    for (k, v) in resp.headers().iter() {
        write!(&mut http_bytes, "{}: {}\r\n", k, v.to_str()?)?;
    }
    http_bytes.extend_from_slice(b"\r\n");

    // body
    let body = resp.bytes().await?;
    http_bytes.extend_from_slice(&body);

    let content_len = http_bytes.len();

    let warc_id = format!("<urn:uuid:{}>", Uuid::new_v4());
    let warc_date = Utc::now().to_rfc3339_opts(SecondsFormat::Secs, true);

    let mut warc_header = Vec::new();
    write!(&mut warc_header, "WARC/1.0\r\n")?;
    write!(&mut warc_header, "WARC-Type: response\r\n")?;
    write!(&mut warc_header, "WARC-Record-ID: {}\r\n", warc_id)?;
    write!(&mut warc_header, "WARC-Date: {}\r\n", warc_date)?;
    write!(&mut warc_header, "WARC-Target-URI: {}\r\n", target_uri)?;
    write!(
        &mut warc_header,
        "Content-Type: application/http; msgtype=response\r\n"
    )?;
    write!(&mut warc_header, "Content-Length: {}\r\n", content_len)?;
    warc_header.extend_from_slice(b"\r\n");

    let mut record = warc_header;
    record.extend_from_slice(&http_bytes);
    record.extend_from_slice(b"\r\n\r\n");

    Ok(record)
}

async fn reduce_warc(
    mut f: BufWriter<File>,
    mut rx: mpsc::Receiver<Vec<u8>>,
    mut pb: Option<Tqdm<()>>,
) -> Result<()> {
    while let Some(warc_bytes) = rx.recv().await {
        f.write_all(warc_bytes.as_ref()).await?;
        if let Some(pb) = pb.as_mut() {
            pb.update(1)?;
        }
    }
    Ok(())
}
