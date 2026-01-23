use anyhow::Result;
use flate2::read::MultiGzDecoder;
use std::{
    fs::File,
    io::{BufReader, BufWriter, Write},
    panic::catch_unwind,
};
use warc::{RecordType, WarcReader};

fn main() -> Result<()> {
    let root_dir = env!("CARGO_MANIFEST_DIR");
    let warc_path =
        format!("{root_dir}/assets/warcs/CC-MAIN-20250417135010-20250417165010-00065.warc.gz");
    let line_path = format!("{root_dir}/assets/warcs/lines.txt");

    let gz_decoder = MultiGzDecoder::new(File::open(warc_path)?);
    let buf_reader = BufReader::new(gz_decoder);
    let warc_reader = WarcReader::new(buf_reader);

    let mut line_writer = BufWriter::new(File::create(line_path)?);

    for record in warc_reader.iter_records() {
        let record = match record {
            Ok(r) => r,
            _ => continue,
        };
        if *record.warc_type() != RecordType::Response {
            continue;
        }

        let warc_bytes = record.body();
        let content_length = record.content_length() as usize;
        let n = warc_bytes.len();
        let html_bytes = &warc_bytes[(n - content_length)..];

        if html_bytes.is_empty() {
            continue;
        }

        let text = match catch_unwind(|| html2text::from_read(html_bytes, 1024)) {
            Ok(Ok(t)) => t,
            _ => continue,
        };

        for line in text.lines().filter(|l| !l.is_empty()) {
            line_writer.write_all(line.as_bytes())?;
            line_writer.write(b"\n")?;
        }
    }

    Ok(())
}
