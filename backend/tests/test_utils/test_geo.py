"""Tests for app.utils.geo."""

from unittest.mock import MagicMock, patch

import pytest

from app.utils.geo import calculate_distance, geocode_address


class TestCalculateDistance:
    def test_same_point_is_zero(self):
        dist = calculate_distance(0, 0, 0, 0)
        assert dist == pytest.approx(0.0, abs=1e-6)

    def test_known_distance_nyc_la(self):
        # NYC to LA is roughly 2445 miles
        dist = calculate_distance(40.7128, -74.0060, 34.0522, -118.2437)
        assert 2400 < dist < 2500

    def test_short_distance(self):
        # Two points very close together
        dist = calculate_distance(37.7749, -122.4194, 37.7750, -122.4195)
        assert dist < 0.1  # less than 0.1 miles


class TestGeocodeAddress:
    def test_returns_none_when_no_token(self, app):
        with app.app_context():
            with patch.dict(app.config, {"MAPBOX_ACCESS_TOKEN": None}):
                result = geocode_address("1600 Pennsylvania Ave NW, Washington, DC")
                assert result is None

    def test_returns_coordinates_on_success(self, app):
        with app.app_context():
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "features": [{"geometry": {"coordinates": [-77.0366, 38.8971]}}]
            }
            with (
                patch("app.utils.geo.requests.get", return_value=mock_response),
                patch.dict(app.config, {"MAPBOX_ACCESS_TOKEN": "fake-token"}),
            ):
                result = geocode_address("1600 Pennsylvania Ave NW")
                assert result == {"lng": -77.0366, "lat": 38.8971}

    def test_returns_none_when_no_features(self, app):
        with app.app_context():
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"features": []}
            with (
                patch("app.utils.geo.requests.get", return_value=mock_response),
                patch.dict(app.config, {"MAPBOX_ACCESS_TOKEN": "fake-token"}),
            ):
                result = geocode_address("Nowhere St")
                assert result is None

    def test_returns_none_on_http_error(self, app):
        with app.app_context():
            mock_response = MagicMock()
            mock_response.status_code = 500
            with (
                patch("app.utils.geo.requests.get", return_value=mock_response),
                patch.dict(app.config, {"MAPBOX_ACCESS_TOKEN": "fake-token"}),
            ):
                result = geocode_address("Bad Address")
                assert result is None
