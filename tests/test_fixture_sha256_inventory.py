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
    "fixtures/blackboard_contract/annotation.invalid_extra_safety_flag.json": "183b92e80ddd1fb4a388b9d1bbecc19d3cea8b0db0d74531a63f9b2aeaa8bd75",
    "fixtures/blackboard_contract/annotation.invalid_missing_common.json": "c93d8f077565696f58baaae2d228ceddb40e809c2e2b9142bf3ff1cdcc364d57",
    "fixtures/blackboard_contract/annotation.valid.json": "e3e458b5ea0e5731a287503185e7400622e64a17b1be0e264464655594ddaf55",
    "fixtures/blackboard_contract/approval_packet.invalid_extra_safety_flag.json": "b4f0c2970d9aecd9644983e2fa56a9890476dde1804b7ffa7ea21741dc1c2a44",
    "fixtures/blackboard_contract/approval_packet.invalid_missing_common.json": "511ad40f4600418e4146339cef74a4df831cbf759e7733c41b1ccc0b23802c40",
    "fixtures/blackboard_contract/approval_packet.valid.json": "9d57ca6baf1aa43bc0ccd7e52bea72d7ac301db59d4bae8e4a7680c082a3e051",
    "fixtures/blackboard_contract/approval_readiness.invalid_extra_safety_flag.json": "596b619dbecc7f3a95723d6570716aa2115a646af591fc074f74a4cd9ba8fa9d",
    "fixtures/blackboard_contract/approval_readiness.invalid_missing_common.json": "8652b65a7f5ab5eeffed206e2690c526f27bcd0857a2bccbcf013f716484865c",
    "fixtures/blackboard_contract/approval_readiness.valid.json": "0331d26c5bc0cd0f7106fc6788b4ba7608b141811019aefbef698dcddec10a63",
    "fixtures/blackboard_contract/audit_event.invalid_extra_safety_flag.json": "b992d7cf1b4e4d5986cb81b72339fe5a760899849e92c8564bb5173c50c9fd26",
    "fixtures/blackboard_contract/audit_event.invalid_missing_common.json": "a8689268513f53e66bb0d458adb78e9593c19eebf2babd7668eb301be9150bcd",
    "fixtures/blackboard_contract/audit_event.valid.json": "31d52647681b0cbecf901497ddd1802cfd747736cbcff4e2fc9beb69b7416bf8",
    "fixtures/blackboard_contract/openclaw_command_envelope.invalid_extra_safety_flag.json": "d8944fa186dc8b7405ebced3b0517d2eec339b34df841aff8a36f9a9967b980f",
    "fixtures/blackboard_contract/openclaw_command_envelope.invalid_missing_common.json": "679e18377a3c363f95cec04921252caf3c8bf92db8811d320d211a51f720c3ca",
    "fixtures/blackboard_contract/openclaw_command_envelope.valid.json": "8b50892fdf8a7d1e5f85bc92cdf6a358f178a36672ec5d265774c96f2b4eb977",
    "fixtures/blackboard_contract/owner_decision.invalid_extra_safety_flag.json": "fc2b9e007c58f9a4aaff79672006fbd140f44bf101418a5b7ffb5560572b171b",
    "fixtures/blackboard_contract/owner_decision.invalid_missing_common.json": "a61e4dfec76982206ce6b941c91aaf8a9122d989236e05886bfb726ecd896031",
    "fixtures/blackboard_contract/owner_decision.valid.json": "18af7d63c2356775a914817ecbe6128a905ff77cd3891cdc2879d91537334b89",
    "fixtures/blackboard_contract/result_message.invalid_extra_safety_flag.json": "d9cd3f912ea0cb76ec3a2bd9260a491d2232a80feac37729e013f43fe4ff6ea7",
    "fixtures/blackboard_contract/result_message.invalid_missing_common.json": "993fe0c3b4a1e6ec6a7a4d91acfaf446ba9a4e4997bb40bfde9a48284122e76d",
    "fixtures/blackboard_contract/result_message.valid.json": "5ec5d1543cb27038cae49a79b9d613b33931c5d59c07d5740208b3de11ee47b8",
    "fixtures/blackboard_contract/rollback_event.invalid_extra_safety_flag.json": "939581e7401d270f21a4a53dca40911f7c81606e78579095f4d72d4748fae07f",
    "fixtures/blackboard_contract/rollback_event.invalid_missing_common.json": "5c36a8e186b3035f558a0a2d285651cb246b475c395c36666dfb3c72bf0890e2",
    "fixtures/blackboard_contract/rollback_event.valid.json": "1e6d304b284ef1c3dfdbd2d8c535ad1c33c1691a575cf2f772765e1b9f57015d",
    "fixtures/blackboard_contract/task_draft.invalid_extra_safety_flag.json": "b4ecaebbdc2eb340055d9cf9ffc062e1298b217d5147f58b4ac3f3ca8957314d",
    "fixtures/blackboard_contract/task_draft.invalid_missing_common.json": "7614933ac7dc32a8481e553b60d0e8d56bc39a92c0a3a817e5fad72afa40db37",
    "fixtures/blackboard_contract/task_draft.valid.json": "47be6450200b3670602129016d0de3a3d99b45aea50baec2de504658595fe8fd",
    "fixtures/blackboard_contract/worker_dry_run.invalid_extra_safety_flag.json": "4fc5721cd95d68db98a27dc7b999cacd97105b88f8a972e66fed5d033951a534",
    "fixtures/blackboard_contract/worker_dry_run.invalid_missing_common.json": "d320fce96ac33651a9985d7140f6d037030914273bda4de89c00cff3d5688365",
    "fixtures/blackboard_contract/worker_dry_run.valid.json": "aca7b26f17be4942af5e8b73d5613dd31dd0ba49a59e6314f2ce057220634a4a",
    "fixtures/builder_golden_vectors/approval_packet_vectors.json": "2f890d850a2f365ec77b094cf5cb845dadfe1666345836f91a257ad4e5c7d5c6",
    "fixtures/builder_golden_vectors/evidence_bundle_vectors.json": "5935dae74a7202648cc97f54a7a44d9abc68f3078187692d2699135e632d9fd8",
    "fixtures/hash_chain_vectors/chain_genesis.json": "90e16dd40a369879758698dbe371c3659273209039e9a3b828329bc33e3cefe7",
    "fixtures/hash_chain_vectors/chain_second.json": "348e3f24faed6e4e243aa76bd125989d6f3049dfd60c13340685524f81dee49a",
    "fixtures/hash_chain_vectors/chain_third.json": "9dd685ee728d6585a2233a891a9f9ce460ac96f308036d94d08ce11edc60ce8c",
    "fixtures/hash_chain_vectors/escaped_text.json": "42ab860cf8601a517f9266cd7086c15848789a77b63ea185add145773c1db3f5",
    "fixtures/hash_chain_vectors/minimal.json": "47f3b84be01b7009624c3794906571a247dc11c4cd92c9084b4215907def3b82",
    "fixtures/hash_chain_vectors/nested_sorting.json": "163588f5346c2c0abfe1da9cf8dbf6fee20df3623e8bbdde2d36f5f0ab5de4ad",
    "fixtures/hash_chain_vectors/types_and_order.json": "62b74bca4ae495ab820dd64d03c17d126e9eda8c2dd112784b432c838963b993",
    "fixtures/hash_chain_vectors/unicode_nfc.json": "6bafee9bd60e39086e5bb1d9eef5d39313bfd1ef3aef773440d9739a2e641f94",
    "fixtures/local_mock_data/hermes_full_blackboard_loop_rehearsal_v1_0_rc_d.json": "f50b8c6e9c5dbfe027f06f70fd5d04dfa535ca0040f7010a470005e7d2b3aacd",
    "fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json": "a52d60120a1d9dc1354c8166fb740153053f117d84863259fd926fddd9f241a1",
    "fixtures/local_mock_data/hermes_openclaw_worker_dry_run_preview_v0_8_3_b.json": "2464f9a6ade9d6f7759c8be92a00eb0b0af9dad67259446bfea0b57f52025e9e",
    "fixtures/local_mock_data/hermes_openclaw_worker_dry_run_result_audit_trail_v0_8_4_b.json": "6bf551e8f263404122940152e4578cd0b92c56eed6151741c59397b2d2bf7700",
    "fixtures/local_mock_data/hermes_result_feedback_preview_v0_9_6_d.json": "a576768fc25c8b6983a742ee1c09c8934130bb452fb985c891f93dc1dc13936b",
    "fixtures/local_mock_data/n1_dry_run_evidence_bundle.json": "0667c6c65ca6120602e5d238c57622d6f3a1ca40635320f401b482eee763a76d",
    "fixtures/local_mock_data/remote_readonly_projection.invalid_extra_payload.json": "c9c1fd99d632119f844e1ef9e9aa3cab958a62a59bdcff3a87d314de53a312b2",
    "fixtures/local_mock_data/remote_readonly_projection.invalid_pulled_at.json": "4abb18a4639e0ba7788097ad544b42bd5b6854eb2a4425f476b2da13ac4a310d",
    "fixtures/local_mock_data/remote_readonly_projection.invalid_secret_value.json": "870354dfead60e54c64812f1d4883573e670147be7accece9acb19168f2d0e26",
    "fixtures/local_mock_data/remote_readonly_projection.valid.json": "07cb13cb2d067080ef13a8a4e86dcf634210621361eee03a3ca72ce4553d9afe",
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
    digest = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
    assert digest == EXPECTED_SHA256[relative_path]
