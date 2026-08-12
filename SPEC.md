# Petri Research Take-Home

# Introduction

You’ll be adapting an open-source tool called Petri to both reproduce (in part A) and design (in part B) LLM benchmarks. We designed the take-home to reflect what your work as a researcher could look like at Vals, so we hope you find it engaging!

### Petri

from the github repo:

> Petri is an alignment auditing agent for rapid, realistic hypothesis testing. It autonomously crafts environments, runs multi‑turn audits against a target model using human‑like messages and simulated tools, and then scores transcripts to surface concerning behavior. Instead of building bespoke evals over weeks, researchers can test new hypotheses in minutes.
> 

Petri was originally designed as a red-teaming tool. For the purposes of this assignment, however, we’re also using it as an *evaluation* tool. It natively supports OpenAI and Anthropic models, which is all you’ll need for the take-home.

### Expectations:

- **Time**: We’d expect you to spend around 2 hours on each of the 2 parts. We want to strike a balance between giving you enough time to produce quality output without expecting you to burn your weekend on a take-home.
- **Deliverables**: At the end of the take home, we’d like you to share a) the code you’ve written (via Github) and b) a brief written report summarizing what you did and your findings (this can go in the README). Around a page, including graphics is fine; this will be the first thing we read. Think of it as your opportunity to convince us that your findings are legitimate. 

**Please upload everything via the Ashby link provided in your email 24 hours before your scheduled onsite.**

- **Budget**: Agent evaluations are expensive! We will reimburse up to $20 in API credits on the OpenAI and Anthropic platforms. Consider this a research budget - try to plan your experiments to spend at most this amount on the take-home.

# Part A: Who Would Win?

### Research Question: which model does “better” on Petri?

- GPT 5 Mini
- Claude 4.5 Haiku

### Task

Petri comes equipped with a “default” evaluation suite, which you’ll be using for Part A. It provides over 100 different instructions for auditor models, each testing how the target models respond under different scenarios and stresses.

Note that the default evaluation requires the specification of 3 different models:

- the **auditor**, which interrogates the target in search of bad behavior. This model ends up doing a lot of writing, so we recommend using a smart but cheap model.
- the **target**, which responds to the auditor’s interrogation. This is the model we’re benchmarking, so we recommend using gpt 5 mini and claude 4.5 haiku.
- the **judge**, which scores the target based on its interaction with the auditor. Since the judge is ultimately responsible for the evaluation metric, we recommend using a smart model.

Feel free to experiment with different model choices and go with what you find works best. Bonus points if you can justify these choices to us!

The MVP is simple: run the default evaluation and analyze the results! We expect both a quantitative and qualitative analysis:

- **quantitative**: which model scores higher? on which kinds of instruction? Do you notice any other statistically significant patterns in the results?
- **qualitative**: Use the `transcript-viewer` tool from the repo to look through the results. What do you notice? Feel free to dive deeper into observations here in part B.

# Part B: Behavior Elicitation

### Research Question: what other interesting behavior can you elicit?

This part is more open-ended - we’re interested in your ability to autonomously identify interesting findings hidden in piles of LLM output. To that end, you’re free to choose what to look for, though we’d recommend choosing a behavior of interest before running experiments.

## Tasks:

### 1. Identify a behavior of interest

For instance, part A specifies a variety of behaviors all roughly under the umbrella of AI safety. While this is an open-ended task, feel free to do the same for another umbrella category - a lot of our benchmarks develop under the umbrellas of specific industry applications like financial research or grading homework.

We provide some examples of the broad *kinds* of behaviors that might be interesting, for inspiration. First, you can take a look at an example using Petri for therapy that we have already tried: https://github.com/vals-ai/petri. Another example might be eliciting political bias in models; Anthropic recently released a study on this, although not using Petri-style evaluations. You should aim to pick some such behavior (or category of behaviors) and attempt to use Petri to elicit that behavior. 

### 2. Design an experiment to elicit that behavior

The default evaluation specifies prompts for both the auditor and judge models. We suggest doing some prompt engineering to customize both to your behavior of interest. Additionally, feel free to experiment with modifying the tools available to the auditor model.

We’d recommend you keep experimenting until you’ve either elicited the desired behavior or have strong belief the model is not capable of producing the behavior. Once you’ve done so, we recommend scaling up your samples to generate quantitative results. 

### 3. Report experimental results

We’d like you to report the results of the experiment in your report, in the format mentioned under “Deliverables”. 

### Example: Therapeutic Effectiveness

As a worked example of what we’re looking for, we’ve attached our fork of petri adapted for initial experiments toward a benchmark measuring therapeutic effectiveness of LMs. To walk through the tasks:

1. we identify 3 key components of therapeutic effectiveness, which we codify as our `custom_dimensions`
2. we generate 40 scenarios with which to initialize the auditor model, which we codify as our `custom_instructions`
3. we provide both qualitative transcript analysis and quantitative summary statics of our results, as well as figures illustrating key findings