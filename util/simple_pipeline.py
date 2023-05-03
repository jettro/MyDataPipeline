import logging
from abc import ABC, abstractmethod

query_pipeline_log = logging.getLogger("pipeline")


class SimplePipeline:
    def __init__(self, steps: list):
        self.steps = steps

    def start_process(self, input_data):
        return self.__process_steps(input_data=input_data, steps=self.steps.copy())

    def __process_steps(self, input_data, steps):
        # Check if there are no more steps to process
        if len(steps) == 0:
            return input_data
        # Get the next step and remove it from the list
        next_step = steps.pop(0)

        query_pipeline_log.info(f"Processing step '{next_step}'")

        # Call the next step with input data
        output_data = next_step.execute_step(input_data)

        # Recursively call process_steps with the output data and remaining steps
        return self.__process_steps(output_data, steps)


class PipelineStep(ABC):
    def __init__(self, name: str, enabled: bool = True):
        self.name = name
        self.enabled = enabled

    @abstractmethod
    def execute_step(self, input_data):
        pass

    def __str__(self):
        return f"Executing step '{self.name}'"


class LogInputPipelineStep(PipelineStep):

    def execute_step(self, input_data):
        query_pipeline_log.info(f"The input looks like this:")
        query_pipeline_log.info(input_data)
        return input_data
