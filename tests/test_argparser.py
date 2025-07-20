
import sys
import pytest
from argparse import ArgumentError, Namespace
from src.argparser import get_args

def run_with_args(args_list):
    """Helper to run get_args with a specific sys.argv list."""
    old_argv = sys.argv.copy()
    sys.argv = ["prog"] + args_list
    try:
        return get_args()
    finally:
        sys.argv = old_argv

def test_persona_required():
    # Should fail if --persona is missing
    old_argv = sys.argv.copy()
    sys.argv = ["prog"]
    with pytest.raises(SystemExit):
        get_args()
    sys.argv = old_argv

def test_minimal_args():
    args = run_with_args(["--persona", "Lilly"])
    assert args.persona == "Lilly"
    assert args.llm_model is None
    assert args.debug is False

def test_all_args():
    args = run_with_args(["--persona", "Lilly", "--llm-model", "qwen3:4b", "--debug"])
    assert args.persona == "Lilly"
    assert args.llm_model == "qwen3:4b"
    assert args.debug is True

def test_debug_flag():
    args = run_with_args(["--persona", "Lilly", "--debug"])
    assert args.debug is True

def test_llm_model_optional():
    args = run_with_args(["--persona", "Lilly", "--llm-model", "llama2"])
    assert args.llm_model == "llama2"
