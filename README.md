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

Example input:

```text
2 beers and 1 whiskey shot

Example output:
Category: mixed
Estimated Alcohol Units: 3.0
Decision: caution
Reason: Your intake is increasing. Consider slowing down, drinking water, and avoiding more alcohol.

The app also includes a lifestyle log that saves each drink entry during the session.
