from ..action.action_result_set import ActionResultSet


class Agent:
    """Run the agent and return True if successful, False otherwise."""
    def run(self, run_config: dict[str, any]) -> ActionResultSet:
        """Subclasses should implement this method."""
        pass
