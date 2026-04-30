# DrankDrunk: AI Alcohol Intake Decision Assistant

## 1. Context, User, and Problem

DrankDrunk is a small GenAI application designed for urban professionals who drink socially and want a low-friction way to estimate alcohol intake in real time.

The workflow I am improving is alcohol intake tracking and decision-making. In the current manual workflow, users need to remember drink size, alcohol percentage, quantity, and then estimate their intake manually. This is inconvenient, especially in a social setting.

The problem matters because alcohol decisions often happen quickly and informally. A simple tool that converts natural-language drink descriptions into estimated alcohol units can help users slow down, reflect, and make safer choices.

## 2. Solution and Design

I built a Streamlit app that allows users to enter drink descriptions in natural language, such as:

- `beer 500ml`
- `whiskey shot`
- `2 beers and 1 whiskey`
- `a couple drinks`

The app uses a language model to classify the drink type and normalize the input into structured JSON. Then, a rule-based calculation estimates alcohol units and produces one of three safety recommendations:

- Continue
- Caution
- Stop

The system design has five steps:

1. User enters a free-text drink description.
2. The LLM converts the input into structured JSON.
3. The app calculates estimated alcohol units.
4. The app applies decision rules.
5. The app saves the result into a simple lifestyle log.

The main GenAI design choice is structured output. The LLM is instructed to return only valid JSON with drink category, estimated ABV, volume, quantity, and confidence level. This makes the output easier to evaluate and safer to use in downstream logic.

GenAI is useful for this task because real drink inputs are often vague or inconsistent. A spreadsheet or form-based baseline requires rigid input, while this app can handle natural expressions such as “a couple drinks” or “one strong cocktail.”

## 3. Evaluation and Results

I evaluated the app using a fixed test set of 20 realistic drink inputs. The test set included simple drinks, cocktails, mixed drinks, and ambiguous inputs.

The baseline was manual spreadsheet tracking. In the baseline workflow, users manually enter drink type, ABV, volume, and quantity before calculating alcohol intake.

Evaluation dimensions:

Metric and What It Measures：

1. Classification Accuracy: Whether the app identifies the correct drink category;
2. Alcohol Estimation Error: Difference between estimated and expected alcohol units;
3. Decision Correctness: Whether the app gives the expected continue/caution/stop recommendation;
4. User Effort: Whether the workflow is easier than manual spreadsheet tracking

In conclusion, the app performed best on common drinks such as beer, wine, and whiskey shots. It also worked reasonably well for common cocktails. The main weaknesses appeared in vague inputs such as “several drinks” or cocktails with unknown strength.

The comparison showed that the app is more convenient than the spreadsheet baseline because users can enter natural language instead of filling out multiple structured fields. However, human judgment is still important because alcohol estimates can be wrong when drink size, strength, or quantity is unclear.

## 4. Artifact Snapshot

This section demonstrates how the application works through real examples.

---

### Example 1: Drink Input & Unit Calculation

Users can manually input drink details, including volume (ml) and alcohol content (%ABV).

Example:
- Drink: Cheese Milk Cap  
- Volume: 100 ml  
- Alcohol Content: 11%  

The system calculates alcohol units directly from these values, ensuring transparency and accuracy without relying on predefined drink categories.

This design allows flexibility for real-world drinks with varying compositions.

![Drink Analyzer](./screenshots/main.png)

---

### Example 2: Session Tracking & Decision Feedback

The system logs each drink within a session and continuously updates total alcohol intake.

Key features:
- Real-time cumulative alcohol units  
- Per-drink breakdown (volume, ABV, timestamp)  
- Immediate decision feedback (Continue / Caution / Stop)

This supports a clear workflow:
input → calculate → accumulate → decision → feedback

The system helps users make safer decisions based on their current intake level.

![Session Log](./screenshots/main.png)

---

### Example 3: Statistics & User Behavior Insights

The statistics dashboard provides insights into drinking behavior over time.

Key features:
- Most frequently consumed drinks  
- Total alcohol units per category  
- Calendar-based consumption patterns  

This transforms raw tracking data into meaningful behavioral insights, supporting long-term awareness.

![Stats](./screenshots/stats.png)

---

### Example 4: Personalized Profile & Limits

The system includes a simple profile and personalization feature:

- Custom username and avatar  
- Adjustable daily alcohol limit  
- Session summary metrics  

The personal limit directly influences decision thresholds:
- Below 50% → Continue  
- 50–85% → Caution  
- Above 85% → Stop  

This demonstrates a personalized workflow tailored to individual users.

![Profile](./screenshots/profile.png)
