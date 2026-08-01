"""Byte-for-byte SHA-256 inventory for every repository fixture.

The guard uses only the standard library and does not import a product hash
helper. Adding, deleting, or changing any fixture requires an explicit review
of this closed table.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest


pytestmark = pytest.mark.contract

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "fixtures"

EXPECTED_SHA256 = {
    "fixtures/blackboard_contract/annotation.invalid_extra_safety_flag.json": "11496f7479cf9865d45605ec48df1f4fe6dc2970a63e0bec18d2ab7814f2dc44",
    "fixtures/blackboard_contract/annotation.invalid_missing_common.json": "4bb15cae36e1452f383b7398e45a1f2c40d1f4813e8df024f2c6207d54a53f80",
    "fixtures/blackboard_contract/annotation.valid.json": "351b446b23b5d649e6e01d8168a3aeb7a8cd158944f474561d61fd0bfee5ecbc",
    "fixtures/blackboard_contract/approval_packet.invalid_extra_safety_flag.json": "4b8f122ae92155fa8ccd6521c06a5e52f525c3fc4eb2a02343e38e9eafdc0b7a",
    "fixtures/blackboard_contract/approval_packet.invalid_missing_common.json": "00026dac37b0ccc55085a1b6ec59b97bfaf0e50edd7b8433f3ea113d2f936212",
    "fixtures/blackboard_contract/approval_packet.valid.json": "5a5dcb74d4ed716c19b8367c26ed73b9ed60bb6a7496e1d3c338d53b1d3f77a5",
    "fixtures/blackboard_contract/approval_readiness.invalid_extra_safety_flag.json": "8d11ddfdc64d434639d65203015df769b50440c64aef80a07c2ba8438ef97542",
    "fixtures/blackboard_contract/approval_readiness.invalid_missing_common.json": "23f4a6b780ae5c6d813bbfe0cbd0533c7c2f3d68fa6be092fd7345d0c85538f2",
    "fixtures/blackboard_contract/approval_readiness.valid.json": "85fb83795cd1b82d844fd707b6bfec3a982bcde3a81d5c6a6dad61860e8ae858",
    "fixtures/blackboard_contract/audit_event.invalid_extra_safety_flag.json": "f07d187964a46ab35a3801551093a1a212545a7ac193e15374697881ff3be794",
    "fixtures/blackboard_contract/audit_event.invalid_missing_common.json": "ae0fdae1a3a23660ca2448d30583ccee30cc4436b89bb7461d0c392cddd3d2d2",
    "fixtures/blackboard_contract/audit_event.valid.json": "19739f8bb7bda3e328d1e8cb6fdb41f59c3e68394f04d0032f894b2f1e46a63f",
    "fixtures/blackboard_contract/openclaw_command_envelope.invalid_extra_safety_flag.json": "ca14d71b129fb530f4693398c6fdff845b034c8c5e254130ccd7e142a032f3a2",
    "fixtures/blackboard_contract/openclaw_command_envelope.invalid_missing_common.json": "d1cfbfe4f00fe9e4d51eae13eefc394a4908c3196f0f26d0d37316a007dc2386",
    "fixtures/blackboard_contract/openclaw_command_envelope.valid.json": "cf5dda55477f2d4263aef078cc28ad0455adf3a549a242ea430f183fec143aa8",
    "fixtures/blackboard_contract/owner_decision.invalid_extra_safety_flag.json": "1014bcf016bf9d4908e56ba71314cc3a8e6a1d2532b490d93760b421c47ff3ed",
    "fixtures/blackboard_contract/owner_decision.invalid_missing_common.json": "be8761439e9a2409f236540d5c247209db4b556e2a8cea4a27c1f9e9a19bd940",
    "fixtures/blackboard_contract/owner_decision.valid.json": "f0fb71d51f871481bdb36e0f85b00edaf0059ecfdfebc1eebba1fd91bb918c2e",
    "fixtures/blackboard_contract/result_message.invalid_extra_safety_flag.json": "8d6d4dbb3967429880be15086a0d0c93dc01ecec83e8912d51a66b3609f66b20",
    "fixtures/blackboard_contract/result_message.invalid_missing_common.json": "14a02aca2f60f371cd2c875fcf180c81e967343eb0f7fe30e0a02164e171088d",
    "fixtures/blackboard_contract/result_message.valid.json": "3cd45a8c3a1374a1a7eacc829929820f0a50dd8a7522717c119b7cc60b4ebce8",
    "fixtures/blackboard_contract/rollback_event.invalid_extra_safety_flag.json": "0fd78ad2677144937045e0ccdcad4baf0340d2cf6ae0b463671fe22dc91b5849",
    "fixtures/blackboard_contract/rollback_event.invalid_missing_common.json": "61eac3d08bfbcabe348016e4774b700a63ec3c6e9f5e46a41de1e7f7bcdc8775",
    "fixtures/blackboard_contract/rollback_event.valid.json": "bb060737103ac5b592e5b52e8e7f9110845111482f4157ec89d97cf1e5ab89fa",
    "fixtures/blackboard_contract/task_draft.invalid_extra_safety_flag.json": "9e720d72abf1b0b1b7f639de4fe832993995647672bc1a5c8542b5c3a7f1b2e1",
    "fixtures/blackboard_contract/task_draft.invalid_missing_common.json": "8544b4d04564fc0bbe031bf2faeb331e4282a5e094d09a187ca33cd2a7279578",
    "fixtures/blackboard_contract/task_draft.valid.json": "98417334189b37d5ebcd573b9fea54cff6809aca1b0d0c13b56dca7f261e01be",
    "fixtures/blackboard_contract/worker_dry_run.invalid_extra_safety_flag.json": "dce22bb1a93558e3aa5a87eb853d4caea8cd5bb48d6ed0caaadc3136378643b5",
    "fixtures/blackboard_contract/worker_dry_run.invalid_missing_common.json": "307ba1da9052b5255b66529f445fc62bf7e3a2870d87b8e2e53cce867bc96b03",
    "fixtures/blackboard_contract/worker_dry_run.valid.json": "184c8e08213a2197ff2a174db2be1c5e1a441614c1e05ee639ed16d03c060cdc",
    "fixtures/builder_golden_vectors/approval_packet_vectors.json": "ac272d431c7b36189ee3d6d08692d9e7772423956880fd942f4f0ce48eb4374a",
    "fixtures/builder_golden_vectors/evidence_bundle_vectors.json": "85a5d1aa8ce54047924bea43d57573cb5d0302ac2b62d334f9dc5a41333a803f",
    "fixtures/hash_chain_vectors/chain_genesis.json": "f7671e6257df700564bd8cb2b0ac103aa3f3a67a9a11ffd3b681f1e7d4be90f9",
    "fixtures/hash_chain_vectors/chain_second.json": "5106501fae2d3d18ac78c4560899710f431a7b7fd35cb1606443380599deb91a",
    "fixtures/hash_chain_vectors/chain_third.json": "7ae8d17321c848c3695a6d4f49a8d835661ef648d0a8645d30e29b7f1cc95f35",
    "fixtures/hash_chain_vectors/escaped_text.json": "0a5efbf6779c0c6c6b5efe6becdae6f63e5ee7acddceee3f97a1cc48300804ba",
    "fixtures/hash_chain_vectors/minimal.json": "78c0387be05cafde1d3152404937f68a23b7633e9b9b4132012754486e3befbf",
    "fixtures/hash_chain_vectors/nested_sorting.json": "a544a2440438eb25e6c1d4b8defa3b37d37ec9ce5d1aaa9d104cb2945e79c1cb",
    "fixtures/hash_chain_vectors/types_and_order.json": "4fa72b52190e551e656def855236ee03ac409c567e5d19d083f9ae3f2f7a6773",
    "fixtures/hash_chain_vectors/unicode_nfc.json": "d5218db1094001bdfce9c625f5d3576f29bbb5137eb017b1d0a072c0c3d0e302",
    "fixtures/local_mock_data/hermes_full_blackboard_loop_rehearsal_v1_0_rc_d.json": "bec8cce6f6a51692a4bd974e2ba1e014f0ddba3d8025eaa648254b86ac553a71",
    "fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json": "d77336ca2be3370efa0da74424ddea9dd4c31adb97d72c359d6e897bfe03579c",
    "fixtures/local_mock_data/hermes_openclaw_worker_dry_run_preview_v0_8_3_b.json": "df9df5807c81dcda09a9e074db38e2bd323091425f60f3a5f7aff1dbb7ad3752",
    "fixtures/local_mock_data/hermes_openclaw_worker_dry_run_result_audit_trail_v0_8_4_b.json": "d4c9b5f1a83bf39849253cd634e415c3c75554fd4127c0fbbc8ebb8a7e9991b9",
    "fixtures/local_mock_data/hermes_result_feedback_preview_v0_9_6_d.json": "b3357ab422159a5f57c7fc6274abe892c2b66eaf2f0ac4ed34f470910350e826",
    "fixtures/local_mock_data/n1_dry_run_evidence_bundle.json": "81c1b6d240da6181a6ae5c7578e4947d8a66fc628f1923bc99d333c95474c64e",
    "fixtures/local_mock_data/remote_readonly_projection.invalid_extra_payload.json": "f54336fb1714cb1c777064e5380ab40166e949788c5f1a178f02e7c8d3f0c0a5",
    "fixtures/local_mock_data/remote_readonly_projection.invalid_pulled_at.json": "c75984a7c2ab4c8ace0cadc75bf22189a7f4509903901e5fdd81c94e521b331f",
    "fixtures/local_mock_data/remote_readonly_projection.invalid_secret_value.json": "6b290779d8d5d24bdac36ca5aacebc817062874c85f38605cb4b8b81c9790653",
    "fixtures/local_mock_data/remote_readonly_projection.valid.json": "11f5238d955121b89c8a96c2778a8c9f7981ade193e79f46ff1364523db031bc",
}


def _fixture_paths() -> set[str]:
    return {
        path.relative_to(ROOT).as_posix()
        for path in FIXTURE_ROOT.rglob("*")
        if path.is_file()
    }


def test_fixture_sha256_inventory_is_exact() -> None:
    assert len(EXPECTED_SHA256) == 50
    assert _fixture_paths() == set(EXPECTED_SHA256)


@pytest.mark.parametrize("relative_path", sorted(EXPECTED_SHA256))
def test_fixture_bytes_match_reviewed_sha256(relative_path: str) -> None:
    data = (ROOT / relative_path).read_bytes().replace(b"\r\n", b"\n")
    digest = hashlib.sha256(data).hexdigest()
    assert digest == EXPECTED_SHA256[relative_path]
