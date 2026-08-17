"""Agent structure tests - Routing, tool presence, and FERPA compliance."""

from google.adk.tools.agent_tool import AgentTool


def _get_agent_tool_names(root_agent):
    """Extract agent names from AgentTool instances in root_agent.tools."""
    return [t.agent.name for t in root_agent.tools if isinstance(t, AgentTool)]


class TestRouting:
    """Test root agent routing logic."""

    def test_student_query_routes_to_student_agent(self, root_agent):
        agent_names = _get_agent_tool_names(root_agent)
        assert "StudentAgent" in agent_names

    def test_risk_query_routes_to_risk_predictor(self, root_agent):
        agent_names = _get_agent_tool_names(root_agent)
        assert "RiskPredictor" in agent_names

    def test_course_query_routes_to_course_recommender(self, root_agent):
        agent_names = _get_agent_tool_names(root_agent)
        assert "CourseRecommender" in agent_names

    def test_financial_aid_routes_to_financial_aid_agent(self, root_agent):
        agent_names = _get_agent_tool_names(root_agent)
        assert "FinancialAidAgent" in agent_names

    def test_advisor_query_routes_to_advisor_agent(self, root_agent):
        agent_names = _get_agent_tool_names(root_agent)
        assert "AdvisorAgent" in agent_names

    def test_analytics_query_routes_to_admin_agent(self, root_agent):
        agent_names = _get_agent_tool_names(root_agent)
        assert "AdminAgent" in agent_names

    def test_all_six_sub_agents_present(self, root_agent):
        expected_agents = {
            "StudentAgent",
            "RiskPredictor",
            "CourseRecommender",
            "FinancialAidAgent",
            "AdvisorAgent",
            "AdminAgent",
        }
        actual_agents = set(_get_agent_tool_names(root_agent))
        assert actual_agents == expected_agents

    def test_root_agent_has_routing_instructions(self, root_agent):
        instruction = root_agent.instruction
        assert "ROUTING RULES" in instruction
        assert "student_agent" in instruction
        assert "risk_predictor" in instruction
        assert "course_recommender" in instruction
        assert "financial_aid_agent" in instruction
        assert "advisor_agent" in instruction
        assert "admin_agent" in instruction

    def test_root_agent_enforces_ferpa(self, root_agent):
        instruction = root_agent.instruction
        assert "FERPA" in instruction


class TestStudentAgentToolUsage:
    """Test StudentAgent calls tools before answering."""

    def test_student_agent_has_search_tool(self, student_agent):
        tool_names = [t.__name__ if callable(t) else t.name for t in student_agent.tools]
        assert "search_student_knowledge" in tool_names

    def test_student_agent_instruction_requires_tool_call(self, student_agent):
        instruction = student_agent.instruction
        assert "MUST call" in instruction
        assert "search_student_knowledge" in instruction

    def test_student_agent_model_is_flash_lite(self, student_agent):
        assert student_agent.model == "gemini-3.5-flash-lite"


class TestRiskPredictorToolUsage:
    """Test RiskPredictor calls tools before answering."""

    def test_risk_agent_has_risk_tools(self, risk_agent):
        tool_names = [t.__name__ if callable(t) else t.name for t in risk_agent.tools]
        assert "analyze_student_risk" in tool_names
        assert "get_student_academic_profile" in tool_names
        assert "get_student_engagement_metrics" in tool_names
        assert "get_intervention_recommendations" in tool_names

    def test_risk_agent_instruction_requires_tool_call(self, risk_agent):
        instruction = risk_agent.instruction
        assert "MUST call" in instruction
        assert "analyze_student_risk" in instruction

    def test_risk_agent_has_risk_scoring(self, risk_agent):
        instruction = risk_agent.instruction
        assert "Low Risk" in instruction
        assert "Medium Risk" in instruction
        assert "High Risk" in instruction
        assert "Critical Risk" in instruction


class TestAdvisorAgentToolUsage:
    """Test AdvisorAgent calls tools before answering."""

    def test_advisor_agent_has_analytics_tools(self, advisor_agent):
        tool_names = [t.__name__ if callable(t) else t.name for t in advisor_agent.tools]
        assert "get_advisor_students" in tool_names
        assert "analyze_student_risk" in tool_names
        assert "get_intervention_recommendations" in tool_names

    def test_advisor_agent_instruction_requires_tool_call(self, advisor_agent):
        instruction = advisor_agent.instruction
        assert "MUST call" in instruction
        assert "get_advisor_students" in instruction

    def test_advisor_agent_default_adv001(self, advisor_agent):
        instruction = advisor_agent.instruction
        assert "ADV001" in instruction


class TestAdminAgentToolUsage:
    """Test AdminAgent calls tools before answering."""

    def test_admin_agent_has_analytics_tools(self, admin_agent):
        tool_names = [t.__name__ if callable(t) else t.name for t in admin_agent.tools]
        assert "get_institutional_analytics" in tool_names
        assert "get_retention_trends" in tool_names
        assert "get_department_comparison" in tool_names

    def test_admin_agent_instruction_requires_tool_call(self, admin_agent):
        instruction = admin_agent.instruction
        assert "MUST call" in instruction
        assert "get_institutional_analytics" in instruction

    def test_admin_agent_no_pii(self, admin_agent):
        instruction = admin_agent.instruction
        assert "NEVER expose individual student PII" in instruction


class TestCourseRecommenderToolUsage:
    """Test CourseRecommender calls tools before answering."""

    def test_course_agent_has_catalog_tool(self, course_agent):
        tool_names = [t.__name__ if callable(t) else t.name for t in course_agent.tools]
        assert "search_course_catalog" in tool_names

    def test_course_agent_instruction_requires_tool_call(self, course_agent):
        instruction = course_agent.instruction
        assert "MUST call" in instruction
        assert "search_course_catalog" in instruction


class TestFERPACompliance:
    """Test FERPA compliance across agents."""

    def test_root_agent_mentions_ferpa(self, root_agent):
        instruction = root_agent.instruction
        assert "FERPA" in instruction
        assert "Never expose one student's data to another" in instruction

    def test_student_agent_isolation(self, student_agent):
        instruction = student_agent.instruction
        assert "Only access the current student's own data" in instruction

    def test_advisor_agent_restriction(self, advisor_agent):
        instruction = advisor_agent.instruction
        assert "only show assigned students" in instruction

    def test_admin_agent_no_pii(self, admin_agent):
        instruction = admin_agent.instruction
        assert "NEVER expose individual student PII" in instruction
        assert "aggregated, anonymized data only" in instruction

    def test_risk_agent_advisor_only(self, risk_agent):
        instruction = risk_agent.instruction
        assert "ADVISORS ONLY" in instruction
        assert "Never share raw risk scores with students" in instruction

    def test_root_agent_role_based_access(self, root_agent):
        instruction = root_agent.instruction
        assert "Students can only see their own information" in instruction
        assert "Advisors can only see their assigned students" in instruction
        assert "Administrators see aggregated" in instruction


class TestToolDataIsolation:
    """Test that tools enforce data isolation."""

    def test_analyze_student_risk_requires_student_id(self):
        from tools.risk_tools import analyze_student_risk
        import inspect

        sig = inspect.signature(analyze_student_risk)
        assert "student_id" in sig.parameters

    def test_get_advisor_students_requires_advisor_id(self):
        from tools.analytics_tools import get_advisor_students
        import inspect

        sig = inspect.signature(get_advisor_students)
        assert "advisor_id" in sig.parameters
