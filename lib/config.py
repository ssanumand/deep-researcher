from math import ceil

from lib.log import logger


class DeepResearchHyperParameters:
    def __init__(
        self,
        num_refinement_questions: int,
        num_learnings: int,
        learning_width: int,
        learning_depth: int,
    ):
        self.num_refinement_questions = num_refinement_questions
        self.num_learnings = num_learnings
        self.learning_width = learning_width
        self.learning_depth = self._cap_learning_depth(learning_depth)

    @property
    def max_allowed_depth(self) -> int:
        return ceil(self.learning_width / 2)

    def _cap_learning_depth(self, depth: int) -> None:
        max_allowed_depth = self.max_allowed_depth

        if depth > max_allowed_depth:
            logger.warning(
                "Depth %d Exceeded for Width %d (capping to: %d)",
                depth,
                self.learning_width,
                max_allowed_depth,
            )
            self._learning_depth = max_allowed_depth
        else:
            self._learning_depth = depth

    def calculate_width_for_depth(self, depth: int) -> int:
        return ceil(self.learning_width / 2**depth)

    def __repr__(self):
        return (
            "DeepResearchHyperParameters("
            f"num_refinement_questions={self.num_refinement_questions}, "
            f"num_learnings={self.num_learnings}, "
            f"learning_width={self.learning_width}, "
            f"learning_depth={self.learning_depth})"
        )
