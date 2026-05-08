"""Constants shared between Python and PowerShell halves of the skill.

Mirror of constants.psd1. Update both files together; a Pester test in
Stage 6 (planned) will assert the two stay in sync.
"""
HUGGINGFACE_CREDENTIAL_TARGET = "IPPF-MEL-Video-HuggingFace"
WHISPER_DEFAULT_MODEL = "large-v3"
VIDEO_SUBPACKAGE_NAME = "video-content-analysis"
