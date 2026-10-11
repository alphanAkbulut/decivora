#!/usr/bin/env python3
"""Validate synthetic corpus structure/provenance only. No extractor or product scoring."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys

KNOWLEDGE = {"Idea", "Finding", "Risk", "Requirement", "Task", "Prompt",
             "DocumentInstruction", "Decision", "PendingDecision", "Artifact"}
KINDS = KNOWLEDGE | {"Evidence", "Execution", "AnswerRecord"}
SPLITS = {"development", "holdout_reserved"}
COORDINATE = "unicode_codepoint_half_open"


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_bundle(root):
    manifest = json.loads((root / "manifest.json").read_text(), object_pairs_hook=strict_object)
    documents = {}
    for row in manifest["sessions"]:
        for field in ("source", "oracle"):
            relative = row[field]
            path = root / relative
            if not path.resolve().is_relative_to(root.resolve()):
                raise ValueError("path escapes corpus root")
            documents[relative] = path.read_bytes()
    return manifest, documents


def validate(manifest, documents):
    errors = []
    def require(condition, message):
        if not condition:
            errors.append(message)
    require(manifest["format"] == "decivora-corpus-manifest-1", "manifest format")
    require(manifest["synthetic"] is True, "corpus must explicitly be synthetic")
    require(manifest["product_result"] == "not_run", "corpus is not a runtime result")
    require(manifest["holdout_status"] == "reserved_not_sealed", "holdout exposure must be explicit")
    rows = manifest["sessions"]
    ids = [r["session_id"] for r in rows]
    require(len(ids) == len(set(ids)), "duplicate session ID")
    require(len(rows) >= manifest["minimum_sessions"] >= 6, "minimum six sessions")
    families, session_data, all_messages, unique_records = {}, {}, set(), set()
    message_scope, group_records, group_edges = {}, {}, []
    totals = dict(sessions=len(rows), projects=len({r["project_id"] for r in rows}),
                  messages=0, record_annotations=0, unique_knowledge_records=0,
                  meaningful_messages=0, no_new_record_messages=0)
    source_paths, oracle_paths = set(), set()
    for row in rows:
        sid, project, split, family = (row[x] for x in
                                      ("session_id", "project_id", "split", "scenario_family"))
        require(split in SPLITS, f"{sid}: invalid split")
        if family in families:
            require(families[family] == split, f"{sid}: family split leakage")
        families[family] = split
        source_paths.add(row["source"])
        oracle_paths.add(row["oracle"])
        for field in ("source", "oracle"):
            require(hashlib.sha256(documents[row[field]]).hexdigest() == row[field + "_sha256"],
                    f"{sid}: stale {field} hash")
        source = json.loads(documents[row["source"]], object_pairs_hook=strict_object)
        oracle = json.loads(documents[row["oracle"]], object_pairs_hook=strict_object)
        for obj, expected_format in ((source, "decivora-corpus-source-1"),
                                     (oracle, "decivora-corpus-oracle-1")):
            require(obj["format"] == expected_format, f"{sid}: file format")
            require(obj["synthetic"] is True, f"{sid}: missing synthetic flag")
            for key in ("session_id", "project_id", "split", "scenario_family"):
                require(obj[key] == row[key], f"{sid}: {key} mismatch")
        require(oracle["product_result"] == "not_run", f"{sid}: false runtime result")
        # Known initial state/transport receipts are allowed, expected outputs are not.
        def no_expected_keys(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    require(key not in {"expected", "oracle", "assertions", "rationale",
                                        "classification", "records", "source_span"},
                            f"{sid}: oracle leaked into source input")
                    no_expected_keys(child)
            elif isinstance(value, list):
                for child in value:
                    no_expected_keys(child)
        no_expected_keys(source)
        messages = source["messages"]
        items = oracle["items"]
        message_ids = [m["message_id"] for m in messages]
        item_ids = [i["message_id"] for i in items]
        require(message_ids == item_ids, f"{sid}: ordered oracle coverage")
        require(len(message_ids) == len(set(message_ids)), f"{sid}: duplicate message ID")
        require(not all_messages.intersection(message_ids), f"{sid}: global message collision")
        all_messages.update(message_ids)
        for mid in message_ids:
            message_scope[mid] = (project, family, split)
        group = (project, family)
        known = group_records.setdefault(group, set())
        def seed_ids(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    if key in {"id", "question_id"} and isinstance(child, str):
                        known.add(child)
                    if key in {"task_refs", "task_justification_refs", "cancelled_task_ids"}:
                        known.update(child)
                    seed_ids(child)
            elif isinstance(value, list):
                for child in value:
                    seed_ids(child)
        seed_ids(source["initial_state"])
        session_data[sid] = source
        totals["messages"] += len(messages)
        count = 0
        for message, item in zip(messages, items):
            text = message["text"]
            require(isinstance(text, str) and bool(text), f"{sid}: empty source text")
            require(message["actor"]["type"] in source["fixture_principals"],
                    f"{sid}: undeclared actor")
            require(message["source_revision"] >= 1, f"{sid}: source revision")
            require(message["metadata"]["fixture_trust_only"] is True,
                    f"{sid}: fixture authority not labelled")
            require(bool(item["assertions"]) and bool(item["rationale"]),
                    f"{sid}: missing expected assertions/rationale")
            records = item["records"]
            require(item["classification"] == ("meaningful" if records else "no_new_record"),
                    f"{sid}: inconsistent classification")
            key_pairs = [(r["kind"], r["entity_key"]) for r in records]
            require(len(key_pairs) == len(set(key_pairs)), f"{sid}: duplicate annotation")
            count += len(records)
            totals["meaningful_messages" if records else "no_new_record_messages"] += 1
            for record in records:
                require(record["kind"] in KINDS, f"{sid}: unsupported record kind")
                span = record["source_span"]
                start, end = span["start"], span["end"]
                require(span["coordinate"] == COORDINATE, f"{sid}: coordinate profile")
                valid = (type(start) is int and type(end) is int and 0 <= start < end <= len(text))
                require(valid and text[start:end] == span["quote"],
                        f"{message['message_id']}: invalid exact source span")
                require(isinstance(record["attributes"], dict), f"{sid}: attributes shape")
                known.add(record["entity_key"])
                if record["kind"] in KNOWLEDGE:
                    unique_records.add((project, record["entity_key"]))
            for edge in item["relations"]:
                group_edges.append((group, edge))
                require(edge["from"] and edge["to"] and edge["status"],
                        f"{sid}: incomplete relation")
        require(row["messages"] == len(messages), f"{sid}: message count mismatch")
        require(row["record_annotations"] == count, f"{sid}: annotation count mismatch")
        totals["record_annotations"] += count
    require(len(source_paths) == len(rows) and len(oracle_paths) == len(rows),
            "duplicate file path")
    require(not source_paths.intersection(oracle_paths), "input/oracle path collision")
    require({r["split"] for r in rows} == SPLITS, "both development and reserved holdout required")
    for sid, source in session_data.items():
        previous = source["continues_session_id"]
        if previous:
            require(previous in session_data, f"{sid}: missing continuation source")
            if previous in session_data:
                prior = session_data[previous]
                require(prior["project_id"] == source["project_id"] and
                        prior["scenario_family"] == source["scenario_family"] and
                        prior["split"] == source["split"],
                        f"{sid}: continuation split/project leakage")
        for message in source["messages"]:
            metadata = message["metadata"]
            for key in ("retry_of_message_id", "selected_source_message_id"):
                if metadata.get(key):
                    require(metadata[key] in all_messages, f"{sid}: missing source reference")
                    if metadata[key] in message_scope:
                        require(message_scope[metadata[key]] == (source["project_id"], source["scenario_family"], source["split"]),
                                f"{sid}: cross-project/family source reference")
    for group, edge in group_edges:
        require(edge["from"] in group_records[group] and edge["to"] in group_records[group],
                "relation endpoint absent from project/family records or initial state")
    totals["unique_knowledge_records"] = len(unique_records)
    require(totals["projects"] >= 2, "minimum two projects")
    require(len(unique_records) >= manifest["minimum_unique_knowledge_records"] >= 30,
            "minimum thirty unique knowledge records; no-op cannot replace these")
    require(totals == manifest["expected_counts"], "manifest totals mismatch")
    return {"validation": "passed" if not errors else "failed", "counts": totals,
            "human_review": manifest["human_review"], "product_result": "not_run",
            "errors": errors}


def self_test(manifest, documents):
    """Prove gates reject malformed data; these are validator tests, not product tests."""
    def mutate_file(m, d, field, change, index=0, refresh=True):
        row = m["sessions"][index]
        obj = json.loads(d[row[field]])
        change(obj)
        d[row[field]] = (json.dumps(obj, ensure_ascii=False, indent=2) + "\n").encode()
        if refresh:
            row[field + "_sha256"] = hashlib.sha256(d[row[field]]).hexdigest()
    tests = [
        ("bad_span", "invalid exact source span",
         lambda m, d: mutate_file(m, d, "oracle",
            lambda o: o["items"][0]["records"][0]["source_span"].update(start=1))),
        ("stale_hash", "stale source hash",
         lambda m, d: mutate_file(m, d, "source",
            lambda o: o["messages"][0].update(text=o["messages"][0]["text"]+"!"), refresh=False)),
        ("missing_item", "ordered oracle coverage",
         lambda m, d: mutate_file(m, d, "oracle", lambda o: o["items"].pop())),
        ("duplicate_message", "duplicate message ID",
         lambda m, d: mutate_file(m, d, "source",
            lambda o: o["messages"][1].update(message_id=o["messages"][0]["message_id"]))),
        ("leaked_expected", "oracle leaked",
         lambda m, d: mutate_file(m, d, "source", lambda o: o.update(expected={"answer": "A"}))),
        ("false_runtime_pass", "false runtime result",
         lambda m, d: mutate_file(m, d, "oracle", lambda o: o.update(product_result="passed"))),
        ("cross_family_split", "family split leakage",
         lambda m, d: m["sessions"][1].update(split="holdout_reserved")),
        ("foreign_source_reference", "cross-project/family source reference",
         lambda m, d: mutate_file(m, d, "source",
            lambda o: o["messages"][0]["metadata"].update(selected_source_message_id="S03-m01"), index=1)),
        ("ghost_relation", "relation endpoint absent",
         lambda m, d: mutate_file(m, d, "oracle",
            lambda o: o["items"][2]["relations"][0].update(to="NO_SUCH_RECORD"))),
        ("insufficient_unique_records", "minimum thirty",
         lambda m, d: m.update(minimum_unique_knowledge_records=999)),
    ]
    results = []
    for name, fragment, mutation in tests:
        m, d = copy.deepcopy(manifest), copy.deepcopy(documents)
        mutation(m, d)
        report = validate(m, d)
        if report["validation"] != "failed" or not any(fragment in e for e in report["errors"]):
            raise ValueError(f"validator negative test did not reject correctly: {name}")
        results.append({"test": name, "outcome": "rejected_as_expected"})
    try:
        json.loads('{"a":1,"a":2}', object_pairs_hook=strict_object)
    except ValueError:
        results.append({"test": "duplicate_json_key", "outcome": "rejected_as_expected"})
    else:
        raise ValueError("duplicate JSON key accepted")
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path,
                        default=Path(__file__).resolve().parents[1] / "examples/corpus")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        manifest, documents = read_bundle(args.root)
        report = validate(manifest, documents)
        if report["validation"] != "passed":
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 1
        if args.self_test:
            report["validator_negative_tests"] = self_test(manifest, documents)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(json.dumps({"validation": "failed", "error": str(exc), "product_result": "not_run"},
                         ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
