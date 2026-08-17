"""Tool data accuracy and intervention quality tests."""


class TestToolDataAccuracy:
    """Test that tools return accurate data structures."""

    def test_analyze_student_risk_returns_required_fields(self, mock_bigquery_risk):
        from tools.risk_tools import analyze_student_risk

        result = analyze_student_risk("STU001")
        assert "student_id" in result
        assert "risk_score" in result
        assert "risk_level" in result
        assert "contributing_factors" in result
        assert "recommendations" in result

    def test_analyze_student_risk_score_is_numeric(self, mock_bigquery_risk):
        from tools.risk_tools import analyze_student_risk

        result = analyze_student_risk("STU001")
        score = result["risk_score"]
        assert isinstance(score, (int, float))
        assert 0 <= score <= 100

    def test_analyze_student_risk_level_valid(self, mock_bigquery_risk):
        from tools.risk_tools import analyze_student_risk

        result = analyze_student_risk("STU001")
        valid_levels = ["low", "medium", "high", "critical"]
        assert result["risk_level"] in valid_levels

    def test_analyze_student_risk_factors_are_list(self, mock_bigquery_risk):
        from tools.risk_tools import analyze_student_risk

        result = analyze_student_risk("STU001")
        assert isinstance(result["contributing_factors"], list)
        assert len(result["contributing_factors"]) > 0

    def test_analyze_student_risk_recommendations_are_list(self, mock_bigquery_risk):
        from tools.risk_tools import analyze_student_risk

        result = analyze_student_risk("STU001")
        assert isinstance(result["recommendations"], list)
        assert len(result["recommendations"]) > 0

    def test_analyze_student_risk_not_found(self, mock_bigquery_risk):
        from tools.risk_tools import analyze_student_risk

        mock_bigquery_risk.return_value = []
        result = analyze_student_risk("NONEXISTENT")
        assert "error" in result

    def test_get_institutional_analytics_returns_retention(self, mock_bigquery_analytics):
        from tools.analytics_tools import get_institutional_analytics

        mock_bigquery_analytics.side_effect = [
            [{"cnt": 1000}],
            [{"risk_level": "low", "cnt": 600}],
            [{"department": "CS", "retention": 0.85, "enrollment": 200}],
            [{"semester": "Fall 2025", "retention": 0.82}],
        ]

        result = get_institutional_analytics()
        assert "retention_rate" in result
        assert "attrition_rate" in result
        assert "risk_distribution" in result
        assert isinstance(result["retention_rate"], (int, float))

    def test_get_department_comparison_returns_departments(self, mock_bigquery_analytics):
        from tools.analytics_tools import get_department_comparison

        mock_bigquery_analytics.return_value = [
            {"department": "CS", "retention": 0.85, "enrollment": 200, "at_risk": 30},
            {"department": "Arts", "retention": 0.70, "enrollment": 150, "at_risk": 45},
        ]

        result = get_department_comparison()
        assert "departments" in result
        assert "highest_retention" in result
        assert "lowest_retention" in result
        assert len(result["departments"]) == 2


class TestInterventionDataAccuracy:
    """Test that intervention recommendations are accurate."""

    def test_get_intervention_recommendations_critical(self):
        from tools.risk_tools import get_intervention_recommendations

        result = get_intervention_recommendations("critical", ["Low GPA", "Poor attendance"])
        assert result["timeline"] == "within 48 hours"
        assert any("Dean" in a for a in result["priority_actions"])

    def test_get_intervention_recommendations_high(self):
        from tools.risk_tools import get_intervention_recommendations

        result = get_intervention_recommendations("high", ["Missing assignments"])
        assert result["timeline"] == "within 7 days"
        assert any("advisor" in a.lower() for a in result["priority_actions"])

    def test_get_intervention_recommendations_medium(self):
        from tools.risk_tools import get_intervention_recommendations

        result = get_intervention_recommendations("medium", ["Low attendance"])
        assert result["timeline"] == "next 14 days"
        assert any("advisor" in a.lower() for a in result["priority_actions"])

    def test_get_intervention_recommendations_low(self):
        from tools.risk_tools import get_intervention_recommendations

        result = get_intervention_recommendations("low", ["Minor dips"])
        assert result["timeline"] == "next 30 days"
        assert any("reinforcement" in a.lower() for a in result["priority_actions"])

    def test_get_intervention_recommendations_includes_factors(self):
        from tools.risk_tools import get_intervention_recommendations

        factors = ["Factor A", "Factor B"]
        result = get_intervention_recommendations("medium", factors)
        assert result["factors"] == factors


class TestInterventionQuality:
    """Test intervention recommendations quality."""

    def test_critical_has_immediate_actions(self):
        from tools.risk_tools import get_intervention_recommendations

        result = get_intervention_recommendations("critical", ["Severe crisis"])
        actions = result["priority_actions"]
        assert any("URGENT" in a or "emergency" in a.lower() or "Dean" in a for a in actions)

    def test_critical_has_mental_health_referral(self):
        from tools.risk_tools import get_intervention_recommendations

        result = get_intervention_recommendations("critical", ["Crisis"])
        actions = result["priority_actions"]
        assert any("mental health" in a.lower() for a in actions)

    def test_high_has_tutoring_enrollment(self):
        from tools.risk_tools import get_intervention_recommendations

        result = get_intervention_recommendations("high", ["Academic struggle"])
        actions = result["priority_actions"]
        assert any("tutoring" in a.lower() for a in actions)

    def test_high_has_financial_aid_check(self):
        from tools.risk_tools import get_intervention_recommendations

        result = get_intervention_recommendations("high", ["Financial stress"])
        actions = result["priority_actions"]
        assert any("financial" in a.lower() for a in actions)

    def test_medium_has_advisor_meeting(self):
        from tools.risk_tools import get_intervention_recommendations

        result = get_intervention_recommendations("medium", ["Declining grades"])
        actions = result["priority_actions"]
        assert any("advisor" in a.lower() for a in actions)

    def test_medium_has_attendance_followup(self):
        from tools.risk_tools import get_intervention_recommendations

        result = get_intervention_recommendations("medium", ["Low attendance"])
        actions = result["priority_actions"]
        assert any("attendance" in a.lower() for a in actions)

    def test_low_has_positive_reinforcement(self):
        from tools.risk_tools import get_intervention_recommendations

        result = get_intervention_recommendations("low", ["Minor concern"])
        actions = result["priority_actions"]
        assert any("positive" in a.lower() or "reinforcement" in a.lower() for a in actions)

    def test_unknown_risk_defaults_to_medium(self):
        from tools.risk_tools import get_intervention_recommendations

        result = get_intervention_recommendations("unknown", ["Unknown factor"])
        assert result["timeline"] == "next 14 days"

    def test_all_interventions_have_timeline(self):
        from tools.risk_tools import get_intervention_recommendations

        for level in ["low", "medium", "high", "critical"]:
            result = get_intervention_recommendations(level, ["Test factor"])
            assert "timeline" in result
            assert result["timeline"] is not None
            assert len(result["timeline"]) > 0

    def test_all_interventions_have_actions(self):
        from tools.risk_tools import get_intervention_recommendations

        for level in ["low", "medium", "high", "critical"]:
            result = get_intervention_recommendations(level, ["Test factor"])
            assert "priority_actions" in result
            assert len(result["priority_actions"]) >= 2

    def test_timeline_urgency_increases_with_risk(self):
        from tools.risk_tools import get_intervention_recommendations

        low = get_intervention_recommendations("low", ["Test"])
        med = get_intervention_recommendations("medium", ["Test"])
        high = get_intervention_recommendations("high", ["Test"])
        crit = get_intervention_recommendations("critical", ["Test"])

        assert "48 hours" in crit["timeline"]
        assert "7 days" in high["timeline"]
        assert "14 days" in med["timeline"]
        assert "30 days" in low["timeline"]
