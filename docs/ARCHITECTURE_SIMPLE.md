# 🧒 PCM Explained Simply - Like You're 5 Years Old!

---

## 🤔 What Does This Project Do?

Imagine you have a **really smart friend** who helps you figure out if something is true or a lie.

When someone tells you:
> "Did you know that eating carrots makes you see in the dark?"

Your smart friend thinks about it, checks their books, maybe asks their parents, and then tells you:
> "Hmm, that's only a LITTLE bit true. Carrots are good for your eyes, but they won't give you night vision like a superhero!"

**That's what our project does with the internet!** 🌐

---

## 🍕 Let's Use a Pizza Analogy!

Think of our project like a pizza restaurant with **5 special chefs**:

```
🍕 CUSTOMER: "I want to know if pineapple belongs on pizza!"
                              |
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  👨‍🍳 CHEF 1: THE CLEANER                                     │
│                                                              │
│  "Let me understand what you're really asking..."           │
│                                                              │
│  Customer said: "Does pinaple go on pizzza?? 🍍🍕😋"         │
│  Chef cleans it: "Does pineapple belong on pizza?"          │
│                                                              │
│  (Fixes spelling, removes emojis, makes it clear)           │
└──────────────────────────────┬──────────────────────────────┘
                               |
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  👨‍🍳 CHEF 2: THE MEMORY KEEPER                               │
│                                                              │
│  "Wait! I think I remember someone asking this before!"     │
│                                                              │
│  🧠 Checks the BIG MEMORY BOOK...                           │
│                                                              │
│  Found? ✅ "Yes! Last week someone asked the same thing!"   │
│         → Uses the old answer (SUPER FAST!)                 │
│                                                              │
│  Not found? ❌ "Never heard this before..."                 │
│         → Needs to look it up (takes longer)                │
└──────────────────────────────┬──────────────────────────────┘
                               |
                    ┌──────────┴──────────┐
                    |                      |
              REMEMBERED!              NEVER HEARD!
              (skip ahead)             (need to search)
                    |                      |
                    |                      ▼
                    |     ┌───────────────────────────────────┐
                    |     │  👨‍🍳 CHEF 3: THE INTERNET SEARCHER │
                    |     │                                    │
                    |     │  "I'll search the internet!"       │
                    |     │                                    │
                    |     │  🔍 Goes to trusted websites:      │
                    |     │  • Snopes (like a truth-detective) │
                    |     │  • Reuters (news reporters)        │
                    |     │  • Scientists                      │
                    |     │                                    │
                    |     │  Brings back: "Here's what I found!│
                    |     └─────────────────┬─────────────────┘
                    |                       |
                    └───────────┬───────────┘
                                |
                                ▼
┌─────────────────────────────────────────────────────────────┐
│  👨‍🍳 CHEF 4: THE JUDGE                                       │
│                                                              │
│  "Let me think about ALL the evidence..."                   │
│                                                              │
│  🤔 Looks at:                                               │
│  • What the memory book said                                 │
│  • What the internet search found                            │
│  • How trustworthy the sources are                          │
│                                                              │
│  Makes a decision:                                           │
│  ✅ TRUE = "Yes, this is correct!"                          │
│  ❌ FALSE = "No, this is wrong/a lie!"                      │
│  ❓ UNCERTAIN = "Hmm, I'm not sure..."                      │
└──────────────────────────────┬──────────────────────────────┘
                               |
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  👨‍🍳 CHEF 5: THE NOTE-TAKER                                  │
│                                                              │
│  "I'll write this down so we remember next time!"           │
│                                                              │
│  📝 Adds to the BIG MEMORY BOOK:                            │
│  • The question that was asked                               │
│  • The answer we gave                                        │
│  • How sure we were                                          │
│  • When we answered it                                       │
│                                                              │
│  Next time someone asks → INSTANT ANSWER! ⚡                │
└─────────────────────────────────────────────────────────────┘
                               |
                               ▼
              🍕 ANSWER TO CUSTOMER:
              "Pineapple on pizza is SUBJECTIVE! 
               Some people love it, some hate it.
               There's no right answer - it's just opinion!"
```

---

## 📁 What Are All These Files?

Think of our project like a **toy box** with different toys inside:

```
📦 Our Project Box
│
├── 🎮 app.py
│   This is the GAME SCREEN!
│   It's the pretty website you click and type in.
│   Like the TV screen when you play video games.
│
├── ⌨️ cli.py  
│   This is the ROBOT CONTROLLER!
│   For grown-ups who like typing instead of clicking.
│   Like controlling a robot with text commands.
│
├── 📋 requirements.txt
│   This is the SHOPPING LIST!
│   It tells us what things to buy before we can play.
│   Like: "We need batteries, tape, and glue!"
│
├── 🔑 .env
│   This is the SECRET KEY BOX!
│   Has passwords to use special internet services.
│   NEVER show this to strangers!
│
├── 📖 README.md
│   This is the INSTRUCTION MANUAL!
│   Tells you how to start playing with the project.
│
└── 🏭 src/ (The Factory!)
    │
    ├── ⚙️ config.py
    │   The SETTINGS REMOTE CONTROL
    │   Changes how things work, like volume on a TV.
    │
    ├── 🚂 pipeline.py
    │   The TRAIN TRACKS
    │   Makes sure each chef works in the right order.
    │   Chef 1 → Chef 2 → Chef 3 → Chef 4 → Chef 5
    │
    ├── 📦 data_ingestion.py
    │   The MEMORY LOADER
    │   Puts starting knowledge into the memory book.
    │   Like teaching a baby its first words!
    │
    └── 👨‍🍳 agents/ (The Chefs!)
        │
        ├── 🧹 normalizer.py - CHEF 1: The Cleaner
        ├── 🧠 retriever.py  - CHEF 2: The Memory Keeper
        ├── 🔍 web_search.py - CHEF 3: The Internet Searcher
        ├── ⚖️ reasoner.py   - CHEF 4: The Judge
        └── 📝 memory.py     - CHEF 5: The Note-Taker
```

---

## 🤷 Why Do We Need a "Memory"?

Imagine your friend gets asked the same question 100 times:

**Without Memory:**
```
Question 1: "Is the Earth round?" → Searches internet → "Yes!" (5 seconds)
Question 2: "Is the Earth round?" → Searches internet → "Yes!" (5 seconds)
Question 3: "Is the Earth round?" → Searches internet → "Yes!" (5 seconds)
...
Question 100: "Is the Earth round?" → Searches internet → "Yes!" (5 seconds)

Total time: 500 seconds 😓
```

**With Memory (Our Way!):**
```
Question 1: "Is the Earth round?" → Searches internet → "Yes!" → 📝 Writes it down!
Question 2: "Is the Earth round?" → 🧠 "I remember!" → "Yes!" (0.2 seconds)
Question 3: "Is the Earth round?" → 🧠 "I remember!" → "Yes!" (0.2 seconds)
...
Question 100: "Is the Earth round?" → 🧠 "I remember!" → "Yes!" (0.2 seconds)

Total time: 25 seconds! ⚡
```

**That's 20 times faster!** 🚀

---

## 🌐 When Do We Search the Internet?

Our project is **smart about when to search**:

### ✅ USE MEMORY (Fast!) when:
- We've seen this question before
- The answer is still fresh (not too old)
- We're pretty sure it's the same question

### 🔍 SEARCH INTERNET (Slower) when:
- Never heard this question before
- The old answer is too old (things might have changed!)
- Not sure if it's really the same question

**Example:**

| Question | What Happens |
|----------|--------------|
| "Is water wet?" | 🧠 Memory! (Always true, never changes) |
| "Is it raining in Delhi?" | 🔍 Search! (Weather changes every day!) |
| "Did humans land on Moon?" | 🧠 Memory! (History doesn't change) |
| "Who won yesterday's cricket match?" | 🔍 Search! (Need fresh info!) |

---

## 🎯 How Does It Decide TRUE or FALSE?

Chef 4 (The Judge) is very careful! Here's how they think:

### Step 1: Look at what we remember
> "Hmm, I've seen similar questions before. They all said FALSE."

### Step 2: Look at what the internet says
> "The internet also says FALSE. Multiple trusted websites agree."

### Step 3: Count the votes
> "Memory says FALSE. Internet says FALSE. That's a lot of evidence!"

### Step 4: Make a decision
> "I'm 92% sure this is FALSE! Here's why..."

---

## 🛠️ What Tools Do We Use?

| Tool | What It Does | Like In Real Life... |
|------|--------------|---------------------|
| **Qdrant** | Stores our memories | A giant filing cabinet in the cloud |
| **Groq** | Our thinking brain | A super-smart calculator |
| **Tavily** | Searches the internet | A librarian who finds books |
| **Gemini** | Reads pictures | Eyes that can read text in photos |
| **Streamlit** | Makes the pretty website | Paint and crayons for the screen |

---

## 🎮 How to Use It?

### The Easy Way (Click!)
1. Open the website
2. Type your question in the box
3. Click "Verify Claim"
4. Read the answer!

### The Grown-Up Way (Type!)
```bash
python cli.py verify "Vaccines cause autism"
```
Output:
```
📋 Claim: Vaccines cause autism
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 Verdict: False
📊 Confidence: 95%
💬 This claim has been thoroughly debunked by scientific studies.
```

---

## 🌟 Why Is This Project Cool?

1. **It LEARNS!** Every time you ask something, it gets smarter.

2. **It's FAST!** Repeated questions get instant answers.

3. **It's HONEST!** It tells you how sure it is (confidence %).

4. **It EXPLAINS!** Not just "true" or "false" but WHY.

5. **It REMEMBERS!** Like having a friend with perfect memory.

---

## 🗺️ The Journey of a Question

Let's follow a question through the whole system:

```
YOU: "Does eating chocolate give you pimples?"

  ↓ (goes to Chef 1: Cleaner)

CLEAN VERSION: "Does eating chocolate cause acne?"

  ↓ (goes to Chef 2: Memory Keeper)

🧠 CHECKING MEMORY... Not found! Never heard this before.

  ↓ (goes to Chef 3: Internet Searcher)

🔍 SEARCHING... Found 5 articles from health websites!

  ↓ (goes to Chef 4: Judge)

⚖️ THINKING... 
   - 3 articles say "NO, chocolate doesn't cause acne"
   - 2 articles say "MAYBE, but diet matters"
   - No trusted source says "YES definitely"

VERDICT: "Mostly FALSE - chocolate alone doesn't cause pimples,
         but overall diet and hygiene matter more!"

  ↓ (goes to Chef 5: Note-Taker)

📝 SAVING... Now we'll remember this for next time!

  ↓

ANSWER RETURNED TO YOU! 🎉
```

---

## 🎁 Summary

**Our project is like a super-smart friend who:**

- 🧹 Understands messy questions
- 🧠 Remembers everything you've asked before
- 🔍 Searches the internet when needed
- ⚖️ Carefully decides what's true or false
- 📝 Writes down answers for next time
- ⚡ Gets faster the more you use it!

**It helps people know what's real and what's fake on the internet!** 🌐✨

---

*Made with ❤️ to help fight fake news and misinformation!*
