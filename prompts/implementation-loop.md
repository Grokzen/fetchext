# Implementation Loop Prompt

All right, lets go on an adventure. You have a roadmap with items in it. Each implementation loops goal is to complete all items within the next release after the one that is most recently cmopleted. I want you to work on this loop until you have completed all items within that release and after completed all items then you can finish up and report back. Each item should be implemented one by one in sequence given the loop below.

First you figure out the next major item to work on based on the roadmap.
Next you analyze the repo current state and you build a plan file. This file should be written to disk and compared to before, it should remain and not be removed. I want all major features to be tracked based on the plans that was used to implement a given feature.
After the plan is made, review and ensure you have all parts there to implement the plan.
Next i want you do start implementing the plan, code, tests, documentation, testing and everything.
Remember that testing is not only pytest but as well testing in the terminal and analyze the output.
When you done the first pass on the code i want you to analyze and review the changes to ensure they are up to the plan you made and to analyze if the implementation could be done better or if there is anything missing within the code that should be added, included or fixed that you either missed to broke.
When you have completed the implementation you finish up by updating copilot instructions and all relevant documentation like the README.md always needs reviewing. If you have a docs/ folder it also needs to be updated each time.
Lastly you git commit the changes, but do not publish things yet.
After you have completed one feature i want you to loop back to the start and start at taking the next item and run this loop again until you have completed the 3 features. Each feature should result in one git commit each at least.

Once the next major version of features is completed, you can finish up and report back. I will publish the git commits myself after a manual review of the commits
