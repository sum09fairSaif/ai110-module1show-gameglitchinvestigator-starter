# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").

--- When I loaded the game website and started playing the game for the very first time ever, I noticed that I was playing the Normal mode of difficulty of the Number Guessing game, which said to guess a number between 1-100 inclusive, so I entered 1. It rejected my guess of 1 and told me to keep going lower, but logically, that should be impossible as otherwise I'll be going outside the specified range. Yet, I entered 0, and then -3, and for both of these inputs, it didn't give me an error message saying my guesses are outside the range, it just kept saying to go lower. Then, I entered 100, and it told me to go higher this time, but logically, I'll still be going outside the range if I do so. I entered 20, and it then told me to go lower than that, so I entered 10, but it still told me to keep guessing a lower number. Then I checked the Developer Debug Info section, and saw that my secret code was 25. Considering how I'd entered 20, it should've hinted me saying to keep going higher, but instead it said otherwise. When I failed the game in the first round, I noticed that after pressing the New Game button to play the game again, it didn't let me play the game again; the button doesn't seem to work as expected. Instead, it kept saying to start the game from scratch again. Also, when I changed the mode of the game to Hard, the accepted range should've been from 1-50 inclusive, yet the message above the input box kept saying to enter between 1-100 inclusive; the upper bound didn't update correctly.

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

--- I used ChatGPT on this project. The AI suggested a fix in the processing of the conditional logic of what to output as a hint message to the player if their guesses was lower or higher than the secret number to be guessed; the AI suggested if guess < secret, if means the the guessed number was too small and so it should prompt the user to enter a higher guess, and vice versa, which it suggested and was the correct logical approach. The AI suggested that when the outcome is "Too High", i.e. the user guessed a number that was way higher than the actual secret number, and if the number of attempts at which the player made that too-high of a guess was an even-numbered attempt number, the AI suggested that points should be docked off, not added, which is misleading. I ignored that suggestion, and then played the game again where at every even-numbered attempts, I made a too large of a guess than the secret code, and it gave me 5 points extra correctly everytime.

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

---I ran the game app and played the game over and over again, multiple times, in all 3 modes, and checked for myself whether the hints it gave back to me were correct and on par with the secret code, and after I won/lost each game, I could correctly replay and start from scratch with a new game from the start, with all game variables reset to the start condition again (attempts, scores, history, etc.), and ensuring a new number was generated as a secret code.
---After fixing the FIXME 2 block in app.py, I ran python -m pytest -q to validate the changes. The test suite showed 3 passing tests that verify the core game logic in logic_utils.py:

test_winning_guess() - checks that when guess equals secret (both 50), the outcome is "Win"
test_guess_too_high() - verifies that guessing 60 when secret is 50 returns "Too High"
test_guess_too_low() - confirms that guessing 40 when secret is 50 returns "Too Low"

What this showed me: Even though I reorganized the guess-checking logic (moving the st.session_state.attempts += 1 to only count valid guesses), the underlying check_guess() function still worked correctly. The tests passed, which meant I didn't break the hint logic or the win/loss detection logic—only fixed when attempts are counted.

---Yes. I suggested running the pytest suite after making the fix to validate that the refactored code didn't break existing functionality. By examining the test file, I identified what each test was checking (comparing guess vs. secret and verifying the correct outcome message), which helped clarify that the bug was in the flow of checking (attempting before validating) rather than in the actual comparison logic itself. This understanding guided the fix toward moving the attempt counter to only trigger on valid guesses, rather than rewriting the core game logic.

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

---Streamlit "reruns" are like the app pressing the "restart" button on itself every time you interact with it. When you type in a text box, click a button, or change a slider, Streamlit re-executes the entire Python script from top to bottom, which means all variables get recreated and reset to their default values, unless you use session state to save them. Session state is like writing things on a sticky note that survives every restart. Without it, the secret number, attempt counter, and game status would all reset every time you submitted a guess. In this project, st.session_state let us "remember" the secret number, attempts, and game status across button clicks and form submissions. In simple terms, reruns are automatic restarts, and session state is the memory that persists through those restarts, which is essential for games or any app that needs to track information over multiple user interactions.

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.

---Habit/Strategy to reuse: Running pytest after making code changes to validate that my fixes don't break existing functionality, combined with manual testing across all modes/scenarios. In this project, running the test suite immediately after fixing the FIXME 2 block gave me confidence that I hadn't introduced new bugs while reorganizing the attempt-counting logic. I'll bring this "test-first validation" habit to future projects to catch regressions early.

What I'd do differently next time with AI: I'd ask the AI more specific and detailed questions upfront, and I'd critically verify every suggestion by running tests or playing through scenarios before implementing it; not just accepting it because it came from an AI. In this project, ChatGPT gave me both correct advice (the inverted hint logic fix) and misleading advice (about point deductions), so I learned that AI suggestions need verification, not blind trust.

How this changed my thinking about AI-generated code: AI-generated code can look syntactically correct and run without errors, but have fundamental logical flaws that only reveal themselves through actual testing and user interaction. I now understand that AI code requires the same level of scrutiny and testing as any code; maybe more, because it can confidently generate plausible-sounding bugs that trap a developer for hours.
