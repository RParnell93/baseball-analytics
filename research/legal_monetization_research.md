# Legal Considerations for Monetizing a Baseball Analytics Platform

**Research Date:** 2026-03-20
**Disclaimer:** This is research, not legal advice. Consult an attorney before making business decisions.

---

## Executive Summary

The realistic risk for a solo creator making original charts and analysis from publicly available baseball data is **low**, provided you follow a few key rules. The biggest legal protections working in your favor:

1. Raw facts and statistics are not copyrightable (Feist v. Rural, NBA v. Motorola)
2. Original analysis and visualizations you create are your own copyrightable work
3. Scraping publicly available data is generally legal after hiQ v. LinkedIn / Van Buren v. US
4. Dozens of baseball analytics creators (UmpScorecards, Pitcher List, Baseball Prospectus, etc.) monetize original analysis built on public data without legal issues

The main risk vectors are: (a) violating specific terms of service, (b) redistributing raw data rather than original analysis, and (c) gambling affiliate compliance in regulated states.

---

## 1. MLB Data Usage Rights (Statcast / Baseball Savant / MLB Stats API)

### What the law says
- **Raw statistics are not copyrightable.** The Supreme Court established in Feist Publications v. Rural Telephone (1991) that facts cannot be copyrighted. The Second Circuit reinforced this in NBA v. Motorola (1997), ruling that real-time sports scores and statistics are uncopyrightable facts.
- **MLB's copyright** covers their specific presentation, compilation, and arrangement of data, not the underlying numbers. The copyright notice on Baseball Savant reads "MLB Advanced Media, LP. All rights reserved" but this covers their website/presentation, not the raw pitch-by-pitch data itself.

### What MLB's terms say
- MLB.com's Terms of Use prohibit scraping, commercial use of their content, and redistribution. However, these are contractual terms, not laws. Violating TOS is a breach of contract, not a crime.
- The MLB Stats API has no published terms of use or access restrictions. It is an undocumented but publicly accessible API with no authentication required. Many tools (MLB-StatsAPI Python package, etc.) use it openly.
- Statcast data is available through Baseball Savant with no login required.

### What people actually do
- **UmpScorecards** uses Statcast pitch data to generate umpire scorecards, runs a Patreon ($2-$25/month tiers), and has never been shut down by MLB. They have 5 paid tiers and significant following.
- **Baseball Prospectus, FanGraphs, Baseball Reference** all use the same underlying data (from MLB's feed) to build commercial products.
- **Numerous Twitter accounts** post Statcast-derived visualizations commercially without issue.
- MLB has generally embraced the analytics community. They created Statcast partly to encourage this kind of engagement.

### Practical risk: LOW
MLB has no history of suing individual analytics creators. Their enforcement has been against companies rebroadcasting live game data or using official logos/trademarks. Creating original visualizations from statistical data is the bread and butter of the baseball analytics community and MLB benefits from it.

---

## 2. FanGraphs Data Usage

### What FanGraphs TOS says
FanGraphs terms explicitly prohibit:
- "You agree not to reproduce, duplicate, copy, sell, trade, resell or exploit for any commercial purposes, any portion of the Service"
- "You agree not to modify, rent, lease, loan, sell, distribute or create derivative works based on the Service or the Software, in whole or in part"

### What this means practically
- FanGraphs TOS prohibits commercial use of their data.
- However, the underlying statistics (batting average, WAR calculations, etc.) are not copyrightable facts. What FanGraphs owns is their specific compilation and proprietary metrics.
- Using FanGraphs as a data source and then creating your own original analysis is a gray area. You're not redistributing their service, but you are using their compiled data commercially.
- **pybaseball** is MIT-licensed (the tool itself is open source), but this only covers the scraping software, not the data it retrieves. The legality of the data depends on the source's terms.

### What people actually do
- Many commercial baseball analytics products use FanGraphs data. Some have licensing agreements.
- Citing FanGraphs as a source while presenting your own analysis is standard practice.
- Nobody has been sued for using FanGraphs stats in their own original analysis.

### Practical risk: LOW-MEDIUM
Risk is low if you: (a) create original analysis rather than republishing raw FanGraphs data, (b) cite FanGraphs as a source, (c) don't scrape aggressively. Risk increases if you directly republish their leaderboards or proprietary metrics (like their specific WAR calculations) in bulk. If you get big enough to matter, FanGraphs is more likely to ask you to get a data license than to sue you.

---

## 3. Web Scraping Legality

### Key legal precedents
- **hiQ v. LinkedIn (9th Cir., 2022):** The Ninth Circuit ruled that scraping publicly available data does not violate the Computer Fraud and Abuse Act (CFAA). Accessing data that is available to anyone with a web browser does not constitute "unauthorized access."
- **Van Buren v. United States (Supreme Court, 2021):** The Supreme Court narrowed the CFAA's "exceeds authorized access" provision, holding it applies only to people who access areas of a computer system they were not entitled to access at all, not to people who misuse data they were authorized to see.
- **The hiQ/LinkedIn case settled in 2024**, but the Ninth Circuit's legal reasoning stands as precedent.

### What this means
- Scraping publicly available websites (no login required) is generally legal under the CFAA.
- Scraping behind a login (like Ottoneu's authenticated pages) is a different, grayer area.
- TOS violations alone are generally not enough to trigger CFAA liability after Van Buren, but could still support a breach of contract claim.
- Aggressive scraping that degrades a service could trigger other legal theories (trespass to chattels, tortious interference).

### Practical risk: LOW
For scraping public baseball stats sites at reasonable rates, the legal risk is minimal. The entire baseball analytics ecosystem depends on this and no enforcement actions have targeted individual analysts.

---

## 4. Sports Data Copyright

### Legal framework
- **Facts are not copyrightable** (Feist v. Rural Telephone, 1991). This includes all raw statistics: batting averages, pitch velocities, home run distances, etc.
- **NBA v. Motorola (2nd Cir., 1997):** The court ruled that transmitting real-time basketball scores did not violate copyright. Sports statistics are uncopyrightable facts. The "hot news" misappropriation doctrine was narrowed to very specific circumstances (essentially real-time score reporting that directly competes with the league's own broadcast).
- **Compilations can have thin copyright protection** on the specific selection and arrangement, but not on the underlying facts. You can use the same data in your own arrangement.

### What MLB can protect
- Trademarks: team names, logos, "Statcast" name, "MLB" branding
- Copyrighted works: their specific articles, graphics, video content
- Broadcast rights: live game footage, audio
- What they CANNOT protect: the statistical facts themselves (pitch speed, exit velocity, batting average, etc.)

### Practical risk: LOW
Creating your own original visualizations from statistical facts is well-protected. Just don't use MLB logos, team wordmarks in commercial contexts, or reproduce their specific copyrighted content.

---

## 5. Fantasy Sports Legal Framework

### Federal law (UIGEA)
The Unlawful Internet Gambling Enforcement Act of 2006 explicitly exempts fantasy sports when:
- All prizes are established and known in advance
- Winning outcomes reflect relative knowledge and skill
- Outcomes are not based on scores of single games or single athlete performances

### What this means for tools
- **Selling fantasy analytics tools is not gambling.** You're selling information/analysis, not operating a gambling platform.
- You don't need a gaming license to sell fantasy sports tools, projections, or analysis.
- Ottoneu itself is a legal fantasy platform under UIGEA.

### Practical risk: VERY LOW
Selling fantasy baseball tools is clearly legal. You're providing analysis, not operating a gambling operation.

---

## 6. Sports Betting Affiliate Compliance

### Regulatory landscape
- Sports betting is legal in 38+ states (as of 2026), each with its own regulatory framework.
- **Affiliate licensing varies by state.** Some states (like New Jersey, Pennsylvania) require affiliates to register with the state gaming commission. Others have no specific affiliate licensing requirements.
- Many sportsbooks handle compliance through their affiliate programs (DraftKings, FanDuel, BetMGM all have affiliate programs with built-in compliance).

### Key requirements
- **FTC disclosure:** You must clearly disclose affiliate relationships. "#ad" or "affiliate link" disclosures are required when promoting sportsbooks for commission.
- **Age restrictions:** Ads cannot target minors. Most states require 21+ for sports betting.
- **State restrictions:** Some states prohibit or restrict gambling advertising. You may need to geo-restrict certain content.
- **Responsible gambling messaging:** Many states require responsible gambling disclosures alongside betting promotions.

### Practical risk: MEDIUM
This is the area with the most regulatory complexity. If you do affiliate marketing for sportsbooks:
- Join established affiliate programs (they provide compliance guidance)
- Always disclose affiliate relationships per FTC rules
- Include responsible gambling messaging
- Don't target minors
- Be aware that some states have specific advertising restrictions

---

## 7. Ottoneu Terms of Service

### What's known
- Ottoneu's terms page returned 404 during research, so specific terms couldn't be verified.
- Ottoneu is built on FanGraphs (ottoneu.fangraphs.com), so FanGraphs' general terms likely apply.
- Ottoneu has a public-facing aspect (league pages are publicly viewable) and authenticated features (lineup management, trading).

### Practical considerations
- Building tools that interact with authenticated Ottoneu features (like your lineup manager) is scraping behind a login, which is legally grayer than scraping public data.
- Ottoneu is a niche community. The practical likelihood of enforcement against a tool that benefits the community is very low.
- If you commercialize Ottoneu-specific tools, reaching out to Niv Shah (Ottoneu creator) for a blessing would be smart and easy.

### Practical risk: LOW
The Ottoneu community is small and collaborative. Direct communication with the platform operators is the best risk mitigation.

---

## 8. Twitter/X Terms of Service

### Key terms
- X TOS prohibits scraping: "crawling or scraping the Services in any form, for any purpose without our prior written consent is expressly prohibited"
- X Developer Agreement defines "Commercial Use" as use by a business or as part of a monetized product/service
- Automated posting requires compliance with X Automation Rules
- The paid API tiers (Basic: $100/month, Pro: $5,000/month) govern automated posting limits

### What people actually do
- Thousands of commercial accounts post automated content on X.
- Baseball analytics accounts (UmpScorecards, etc.) post automated visualizations daily.
- Affiliate links in tweets are common and not specifically prohibited.
- The key is using the official API for automation rather than scraping.

### Practical risk: LOW-MEDIUM
Use the official API for automated posting. Don't scrape X. Disclose commercial relationships. The main risk is account suspension (not legal action) if you violate automation rules.

---

## 9. API Terms of Service Violations - Enforcement Cases

### Notable cases
- **MLB Advanced Media** has historically been aggressive about protecting live game data and broadcast content, but not about statistical analysis.
- **Sportradar** and other official data providers have sent cease-and-desist letters to companies scraping their APIs, but these target commercial competitors, not individual analysts.
- **ESPN** has shut down unauthorized API users, again targeting apps that replicate their service.
- No known cases of individual baseball analysts being sued for using publicly available statistical data.

### Pattern of enforcement
Sports leagues and data companies enforce against:
1. Companies that directly compete with their data products
2. Rebroadcasting live game data
3. Using trademarks/logos without permission
4. Large-scale commercial redistribution of raw data

They generally do NOT enforce against:
1. Individual analysts creating original content
2. Small-scale tools for niche communities
3. Academic or educational use
4. Content that promotes engagement with their sport

### Practical risk: VERY LOW for your use case

---

## 10. Fair Use / Transformative Work

### Legal framework
- **Fair use** (17 U.S.C. 107) considers: (1) purpose/character of use, (2) nature of copyrighted work, (3) amount used, (4) market effect.
- **But you likely don't even need fair use.** Raw statistics are facts, which are not copyrightable. Fair use is a defense to copyright infringement, and you're not infringing copyright by using uncopyrightable facts.
- Your original visualizations, analysis, and commentary ARE your own copyrightable works. You own what you create.

### The transformative work angle
Even if someone argued the data compilation was copyrighted:
- Original charts and visualizations from raw data are clearly transformative
- Adding analysis and commentary strengthens the transformative use argument
- Your work doesn't substitute for the original data source (people don't stop visiting Baseball Savant because of your charts)

### Practical risk: VERY LOW
Creating original analysis from statistical facts is about as safe as it gets legally.

---

## 11. Sports Betting Advertising Regulations

### FTC requirements
- Must clearly and conspicuously disclose material connections (affiliate relationships)
- Disclosures must be in the same medium as the endorsement (on the tweet itself, not buried in a bio)
- "#ad" or "Affiliate link" or similar clear language
- Cannot make deceptive claims about gambling outcomes

### State-level considerations
- States with legal sports betting each have their own advertising rules
- Common requirements: responsible gambling messaging, no targeting minors, no misleading odds claims
- Some states (e.g., Massachusetts, New York) have strict advertising standards
- Many states require operators (not affiliates) to be licensed, but some require affiliate registration

### Practical approach
- Work through established affiliate programs
- Always include FTC disclosures on affiliate content
- Add responsible gambling messaging
- Don't make claims about guaranteed wins or outcomes

### Practical risk: MEDIUM
The regulatory patchwork is the main challenge. Following FTC rules and working through established affiliate programs mitigates most risk.

---

## 12. Business Structure

### LLC vs. Sole Proprietorship

**Sole Proprietorship:**
- No formation required (you're automatically one when you start earning)
- No liability separation between personal and business assets
- Simpler taxes (Schedule C on personal return)
- Fine for testing/early stages

**LLC:**
- Requires state registration (typically $50-$500 depending on state)
- Separates personal assets from business liabilities
- Same tax treatment as sole proprietorship by default (pass-through)
- Recommended once you're generating meaningful revenue

### Recommendation
- Start as sole proprietorship while testing and building
- Form an LLC once revenue exceeds ~$1,000/year or you start affiliate marketing (higher liability exposure)
- An LLC is cheap insurance against someone suing over content
- Get a separate business bank account regardless of structure

### Practical risk of NOT having an LLC: LOW-MEDIUM
The risk increases with affiliate marketing and subscription revenue.

---

## 13. Tax Implications

### Self-employment tax
- **Rate:** 15.3% on net self-employment income (12.4% Social Security + 2.9% Medicare)
- **Threshold:** Must file if net SE income is $400 or more
- **Deduction:** Can deduct 50% of SE tax as an adjustment to income
- **Additional Medicare:** Extra 0.9% on combined income over $200,000 (single filer)

### Filing requirements
- Report on Schedule C (Profit or Loss from Business)
- Pay SE tax on Schedule SE
- Make quarterly estimated tax payments if you expect to owe $1,000+ in taxes

### Multi-state affiliate considerations
- Most states tax income earned by their residents regardless of where the affiliate company is located
- You generally only need to file in your state of residence for affiliate/subscription income
- No nexus issues from simply having subscribers in other states (you're not selling physical goods)

### Deductible expenses
- Web hosting, domain names, API costs
- Software subscriptions (Streamlit, data services)
- Home office deduction (if applicable)
- Computer/equipment used for the business
- Conference attendance, books, educational materials

---

## Risk Assessment Matrix

### LOW RISK (Go ahead, standard precautions)

| Activity | Notes |
|----------|-------|
| Creating original visualizations from Statcast/public data | Facts are not copyrightable. This is core baseball analytics community activity. |
| Posting original charts on Twitter/X | Thousands of accounts do this commercially. |
| Selling subscriptions to original analysis | Your analysis is your own IP. UmpScorecards, Pitcher List, etc. all do this. |
| Using pybaseball to gather data | MIT-licensed tool. The data itself is public facts. |
| Building fantasy baseball tools | Clearly legal under UIGEA. Not gambling. |
| Using MLB Stats API | No authentication required, no published restrictions, widely used. |
| Running a Patreon/subscription for analytics content | Standard monetization for analytics creators. |

### MEDIUM RISK (Proceed with precautions)

| Activity | Notes |
|----------|-------|
| Using FanGraphs data in commercial products | Their TOS prohibits commercial use. Mitigate by using alternative data sources where possible, creating clearly transformative analysis, and attributing sources. |
| Sports betting affiliate marketing | Regulated space. Use established programs, FTC disclosures, responsible gambling messaging. |
| Automated posting on X | Must use official API. Risk is account suspension, not legal action. |
| Scraping authenticated Ottoneu pages for commercial tools | Behind a login. Talk to Niv Shah for permission. |
| Operating without an LLC while earning affiliate income | Personal liability exposure. |

### HIGH RISK (Avoid or get legal counsel first)

| Activity | Notes |
|----------|-------|
| Republishing raw FanGraphs leaderboards/data in bulk | This crosses from analysis into data redistribution. |
| Using MLB logos, team wordmarks in commercial products | Trademark infringement. |
| Rebroadcasting live game data | This is what MLB actually enforces. |
| Running a gambling affiliate program without FTC disclosures | FTC can and does fine people for undisclosed affiliate relationships. |
| Scraping at high rates that degrade service performance | Could trigger trespass to chattels or tortious interference claims. |

---

## Specific Recommendations

### Immediate (do now)
1. **Attribute your sources.** Credit Baseball Savant, FanGraphs, etc. in your visualizations. This is both ethical and risk-reducing.
2. **Add a disclaimer** to your site/profile: "Not affiliated with MLB, FanGraphs, or Ottoneu. Statistics sourced from publicly available data."
3. **Use FTC-compliant disclosures** on any affiliate content from day one.
4. **Rate-limit your scraping.** Be a good citizen. Don't hammer endpoints.

### Short-term (before generating meaningful revenue)
5. **Form an LLC** once you're earning $1,000+/year. Cost is minimal, protection is real.
6. **Get a separate bank account** for business income/expenses.
7. **Set up quarterly estimated tax payments** once income is consistent.
8. **Contact Ottoneu/Niv Shah** if you plan to commercialize Ottoneu-specific tools. A quick email asking permission is the best legal protection.

### Medium-term (scaling up)
9. **Consider a FanGraphs data license** if your product relies heavily on their data. Or shift to Statcast/Baseball Savant as your primary source (no commercial use restrictions on facts).
10. **For sports betting affiliates,** join established programs (DraftKings, FanDuel) that provide compliance guidance and handle state-by-state registration.
11. **Keep records** of all income and expenses for tax purposes.
12. **Consult a lawyer** if annual revenue exceeds $10K+ or you receive any cease-and-desist communication.

### What other creators actually do
- **UmpScorecards:** Uses Statcast data, runs Patreon ($2-$25/month tiers), posts on Twitter daily. No known legal issues.
- **Pitcher List:** Commercial website with original analysis, community features. Sources from public data.
- **Baseball Prospectus:** Full commercial operation built on statistical analysis.
- **Countless Twitter analytics accounts:** Post original visualizations from public data, many with Patreon or Ko-fi links.

The baseball analytics community has operated this way for 20+ years. MLB has never gone after analysts creating original content from public statistics. The sport actively benefits from this engagement, and MLB knows it.

---

## Bottom Line

For your specific situation (solo creator making original charts and analysis from public data, posting on Twitter, potentially selling subscriptions):

**You are in a well-established, low-risk lane.** The baseball analytics community has been doing exactly this for two decades. The key legal protections (facts aren't copyrightable, scraping public data isn't a crime, original analysis is your own IP) are strong and well-tested.

The areas requiring the most care are: (1) FTC compliance for any affiliate marketing, (2) not republishing raw data in bulk, and (3) forming an LLC once revenue is meaningful. Everything else is standard practice for baseball analytics creators.
