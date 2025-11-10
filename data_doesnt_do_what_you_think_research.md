# Research Summary: "Data Doesn't Do What You Think"

## Executive Summary
"Data Doesn't Do What You Think" is an internal Google document referenced in the leaked May 2023 memo "We Have No Moat, And Neither Does OpenAI" by Luke Sernau. The document has **never been publicly released** and the internal link is dead. However, I've identified likely related public research and the broader context of its arguments.

## What We Know

### 1. **The Reference**
- **Source**: Leaked Google memo "We Have No Moat" by Luke Sernau (May 2023)
- **Context**: The memo states: "These datasets are built using synthetic methods (e.g. filtering the best responses from an existing model) and scavenging from other projects, neither of which is dominant at Google. Fortunately, these high quality datasets are open source, so they are free to use. The existence of such datasets follows from **the line of thinking in Data Doesn't Do What You Think**."
- **Status**: Internal Google link was included in the leaked memo but is now dead/inaccessible
- **Public Release**: No evidence of public release or leak

### 2. **Core Thesis (Inferred)**
Based on context from the "We Have No Moat" memo, "Data Doesn't Do What You Think" likely argues:
- **Data quality scales better than data size**
- Small, highly curated datasets outperform massive datasets
- Synthetic data and careful curation matter more than raw volume
- Traditional assumptions about data scaling laws may be wrong

### 3. **Community Interest**
- Twitter user @aronchick publicly requested Google to publish it (May 2023)
- Discussion on Blind (internal tech forum) asking if Googlers had read it
- Multiple Hacker News threads mention it but no one has shared details
- General consensus: the document exists but wasn't leaked beyond the reference

## Likely Related Public Research

### **Google/DeepMind Publications on Similar Themes:**

1. **"Data Excellence for AI: Why Should You Care"** (2022)
   - **Authors**: Lora Aroyo, Matt Lease, Schaekermann, Paritosh (Google)
   - **Published**: ACM Interactions 2022
   - **Key Arguments**:
     - Data quality has been systematically undervalued
     - Industry focuses on "cost, size, and speed" over "maintainability, reliability, validity, and fidelity"
     - ML has reached an inflection point where data quality will significantly accelerate progress
   - **Similarity**: Nearly identical thesis to what "Data Doesn't Do What You Think" supposedly argues

2. **"Achieving 10,000x training data reduction with high-fidelity labels"** (August 2025)
   - **Authors**: Markus Krause, Nancy Chang (Google Ads)
   - **Published**: Google Research Blog
   - **Key Results**:
     - Reduced training data from 100,000 to <500 examples
     - Increased model alignment by 65%
     - Production systems achieved 4 orders of magnitude reduction
   - **Key Finding**: "Label quality above .8 pairwise Cohen's Kappa is needed to reliably outperform crowdsourced data"
   - **Note**: This is from 2025, so it's newer research, but demonstrates Google has continued this line of thinking

3. **Chinchilla Scaling Laws** (March 2022)
   - **Authors**: DeepMind team
   - **Paper**: "Training Compute-Optimal Large Language Models"
   - **Key Finding**: Models should scale training tokens equally with parameters
   - **Implication**: Quality and efficiency of data usage matters more than previously thought

## The Author of "We Have No Moat"

**Luke Sernau**
- **Position**: Senior Engineer at Google DeepMind (as of 2023)
- **Background**: Mathematics and Machine Learning
- **Career**: Joined Google in March 2019, previously 4 years at Meta on ML infrastructure
- **LinkedIn**: linkedin.com/in/luke-sernau-40394648/
- **Google Scholar**: scholar.google.com/citations?user=Zsi-vgoAAAAJ
- **Note**: Sernau wrote "We Have No Moat" internally in early April 2023, shared thousands of times among Googlers, then leaked via SemiAnalysis in May 2023

## Why "Data Doesn't Do What You Think" Matters

The leaked memo references this document in the context of explaining why open-source was rapidly catching up to Google:

> "Many of these projects are saving time by training on small, highly curated datasets. This suggests there is some flexibility in data scaling laws. The existence of such datasets follows from the line of thinking in Data Doesn't Do What You Think, and they are rapidly becoming the standard way to do training outside Google."

**The Implication**: If small, high-quality datasets can match or beat massive proprietary datasets, then Google's data moat disappears. This was a central concern of the "We Have No Moat" memo.

## Open Source Context (2023)

The memo highlighted how open-source achieved comparable results with tiny budgets:
- **Vicuna**: $300 training cost, ~13B params, claimed "parity" with Bard
- **Koala**: $100 training cost, humans preferred it to ChatGPT >50% of the time
- **GPT4All**: $100 training cost
- **Alpaca-LoRA**: Trained "within hours on a single RTX 4090"

All of these used:
- Small, curated datasets
- Synthetic data (e.g., scraped ChatGPT conversations from ShareGPT)
- LoRA fine-tuning (extremely cheap)
- Quality over quantity

## Conclusion

**"Data Doesn't Do What You Think" has never been publicly released.** However, its core thesis—that data quality matters more than data quantity, and that small curated datasets can outperform massive ones—is well-documented in public Google research from the same period (2022-2023).

The most likely candidates for related public work are:
1. **"Data Excellence for AI: Why Should You Care"** (2022) - Nearly identical arguments
2. **Chinchilla scaling laws research** (2022) - Showed efficient data usage matters
3. **Google's recent work on data reduction** (2025) - Continues the same line of research

If you want to understand what "Data Doesn't Do What You Think" likely argued, reading the "Data Excellence for AI" paper and the Chinchilla research would give you the best approximation.

## Research Attempts

**What I Tried:**
- ✅ Web searches for the document title
- ✅ Archive.org searches (inconclusive, tool errors)
- ✅ Hacker News, Reddit, Blind discussions
- ✅ Twitter mentions
- ✅ Luke Sernau's publications and profile
- ✅ Related Google research papers
- ✅ Academic papers on data quality vs quantity (2022-2023)

**Status**: No public version found, link is dead, author unknown, content never leaked.

## References

- SemiAnalysis: "Google 'We Have No Moat, And Neither Does OpenAI'" (May 2023)
- Aroyo et al.: "Data Excellence for AI: Why Should You Care" (ACM Interactions 2022)
- DeepMind: "Training Compute-Optimal Large Language Models" (Chinchilla paper, March 2022)
- Google Research Blog: "Achieving 10,000x training data reduction" (Aug 2025)
- ACM Communications: "Data Quality May Be All You Need" (references Google DeepMind research)

---

**Last Updated**: November 10, 2025
**Researcher**: Claude (Anthropic)
**Request**: jakesimonds
