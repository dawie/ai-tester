Recommended ways to run Playwright tests
Option A – Headless (default in CI)
Simply use normal pytest and Playwright will run headless:

bash
docker run -it --rm -v ${PWD}:/app ai-tester pytest tests/ai_generated_tests.py
That executes the Playwright tests in Chromium without opening UI windows.

Option B – Headed (see the browser)
To see the browser UI you need to use the Playwright CLI to run and add the headed flag:

bash
docker run -it --rm -v ${PWD}:/app \
  --ipc=host --env DISPLAY ai-tester \
  playwright test tests/ai_generated_tests.py --headed