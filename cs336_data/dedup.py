import random
import shutil
import unicodedata
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path

import xxhash
from regex import Regex


def exact_line_deduplication(input_files: list[str], output_directory: str):
    freq_table: defaultdict[bytes, int] = defaultdict(int)

    for input_file in input_files:
        input_file = Path(input_file)
        with open(input_file) as in_f:
            for line in in_f.readlines():
                line = line.rstrip()
                if not line:
                    continue
                freq_table[hash128(line)] += 1

    for input_file in input_files:
        input_file = Path(input_file)
        output_file = Path(output_directory).joinpath(input_file.name)
        with input_file.open("r", encoding="utf-8") as in_f, output_file.open("w", encoding="utf-8") as out_f:
            for line in in_f.readlines():
                line = line.rstrip()
                if not line:
                    continue
                hash = hash128(line)
                if freq_table[hash] == 1:
                    _ = out_f.write(line + "\n")


def hash128(x: bytes | str):
    if isinstance(x, str):
        x = x.encode()
    return xxhash.xxh3_128(x).digest()


class MinHash:
    def __init__(self, num_hashes: int, ngrams: int) -> None:
        self.num_hashes: int = num_hashes
        self.ngrams: int = ngrams

    def sig(self, doc: str):
        ngrams: set[str] = set()
        n = len(doc)
        for w in range(n + 1 - self.ngrams):
            x = "".join(doc[w : (w + self.ngrams)])
            ngrams.add(x)

        signature: list[int] = []

        for i in range(self.num_hashes):
            h = (1 << 64) - 1
            for ngram in ngrams:
                h = min(h, xxhash.xxh64_intdigest(ngram, i))
            signature.append(h)

        return signature


def normalize_document(doc: str):
    # lowercase
    doc = doc.lower()
    # NFD unicode normalization
    doc = unicodedata.normalize("NFD", doc)
    # remove accents
    doc = Regex(r"[^\x00-\x7F]+").sub("", doc)
    # remove punctuation
    doc = Regex(r"[.!?,\-:;\"\'()]|\s+").sub(" ", doc)
    # normalize whitespace
    doc = Regex(r"\s+").sub(" ", doc).strip()
    return doc


def ngrams_set(doc: str, ngrams: int):
    return {doc[i : i + ngrams] for i in range(len(doc) + 1 - ngrams)} if len(doc) >= ngrams else {doc}


def jaccard_similarity(doc1: str, doc2: str, ngrams: int) -> float:
    s1 = ngrams_set(doc1, ngrams)
    s2 = ngrams_set(doc2, ngrams)
    if not s1 and not s2:
        return 1.0
    inter = len(s1 & s2)
    union = len(s1 | s2)
    return inter / union


class UnionFind:
    def __init__(self, n: int):
        self.parent: list[int] = list(range(n))
        self.rank: list[int] = [0] * n

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: int, b: int):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1


def pairs_to_clusters(n_docs: int, pairs: Iterable[tuple[int, int]]) -> list[set[int]]:
    uf = UnionFind(n_docs)
    for i, j in pairs:
        uf.union(i, j)

    groups: defaultdict[int, set[int]] = defaultdict(set)
    for i in range(n_docs):
        groups[uf.find(i)].add(i)

    return list(groups.values())


def minhash_deduplication(
    input_files: list[str],
    num_hashes: int,
    num_bands: int,
    ngrams: int,
    jaccard_threshold: float,
    output_directory: str,
):
    assert num_hashes % num_bands == 0
    min_hasher = MinHash(num_hashes, ngrams)

    # ----------------------- pass 1: read documents + minhash -----------------------
    sigs: list[list[int]] = []
    norm_docs: list[str] = []
    for in_path in [Path(f) for f in input_files]:
        with open(in_path, encoding="utf-8", errors="replace") as in_f:
            doc = in_f.read()
        doc = normalize_document(doc)
        norm_docs.append(doc)
        sigs.append(min_hasher.sig(doc))

    # ------------------- pass 2: LSH banding, build candidate pairs -------------------
    # key: (band index, band signature)
    # value: list of doc indices
    buckets: defaultdict[tuple[int, int], list[int]] = defaultdict(list)
    rows_per_band = num_hashes // num_bands

    for idx, sig in enumerate(sigs):
        for b in range(num_bands):
            start = b * rows_per_band
            end = (b + 1) * rows_per_band
            band = sig[start:end]
            band_hash = hash(e for e in band)
            buckets[(b, band_hash)].append(idx)

    # candidate duplicate docs (doc index, doc index)
    candidate_pairs: set[tuple[int, int]] = set()
    for doc_indices in (v for v in buckets.values() if len(v) > 1):
        n_dup_docs = len(doc_indices)
        doc_indices = sorted(doc_indices)
        for i in range(n_dup_docs):
            for j in range(i + 1, n_dup_docs):
                candidate_pairs.add((doc_indices[i], doc_indices[j]))

    # ---------------------- pass 3: Calculate Jaccard Similarity ----------------------
    for i, j in list(candidate_pairs):
        if jaccard_similarity(norm_docs[i], norm_docs[j], ngrams) < jaccard_threshold:
            candidate_pairs.remove((i, j))
    clusters: list[set[int]] = pairs_to_clusters(len(norm_docs), candidate_pairs)
    to_dedup: set[int] = set(idx for set in clusters for idx in set)
    keep_docs: list[int] = []

    for i in range(len(input_files)):
        if i not in to_dedup:
            keep_docs.append(i)

    for cluster in clusters:
        keep_docs.append(random.choice(tuple(cluster)))

    for idx in keep_docs:
        in_path = Path(input_files[idx])
        out_path = Path(output_directory) / in_path.name
        _ = shutil.copy2(in_path, out_path)
