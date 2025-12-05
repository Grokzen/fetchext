# Implementation Loop Prompt

All right, lets go on an adventure. You have a roadmap with items in it. This round i want you to complete all items within the 0.5.0 version you have specified. I want you to work in the the following loop to complete these 3 items one by one.

First you figure out the next major item to work on based on the roadmap.
Next you analyze the repo current state and you build a plan file. This file should be written to disk and compared to before, it should remain and not be removed. I want all major features to be tracked based on the plans that was used to implement a given feature.
After the plan is made, review and ensure you have all parts there to implement the plan.
Next i want you do start implementing the plan, code, tests, documentation, testing and everything.
Remember that testing is not only pytest but as well testing in the terminal and analyze the output.
When you have completed the implementation you finish up by updating copilot instructions and all relevant documentation.
Lastly you git commit the changes, but do not publish things yet.
After you have completed one feature i want you to loop back to the start and start at taking the next item and run this loop again until you have completed the 3 features. Each feature should result in one git commit each at least.

Once the next major version of features is completed, you can finish up and report back. I will publish the git commits myself after a manual review of the commits
