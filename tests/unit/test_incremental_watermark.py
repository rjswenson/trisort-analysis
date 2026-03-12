from app.sync.incremental_sync import compute_updated_since, determine_watermark_out


def test_compute_updated_since_applies_lookback() -> None:
	updated_since = compute_updated_since(
		last_watermark="2026-03-10T12:00:00+00:00",
		lookback_days=7,
		fallback_start_date="2026-01-01",
	)
	assert updated_since.startswith("2026-03-03")


def test_compute_updated_since_falls_back_when_missing_watermark() -> None:
	updated_since = compute_updated_since(
		last_watermark=None,
		lookback_days=7,
		fallback_start_date="2026-01-01",
	)
	assert updated_since == "2026-01-01"


def test_determine_watermark_out_uses_max_updated_value() -> None:
	issues_rows = [
		{"updated_at": "2026-03-01T10:00:00+00:00"},
		{"updated_at": "2026-03-02T10:00:00+00:00"},
	]
	assert determine_watermark_out(issues_rows, fallback="2026-02-01") == "2026-03-02T10:00:00+00:00"


def test_determine_watermark_out_uses_fallback_on_empty_set() -> None:
	assert determine_watermark_out([], fallback="2026-02-01T00:00:00+00:00") == "2026-02-01T00:00:00+00:00"
