![banner](images-for-readme/videogames_banner.jpg)

# Video Games Market Analysis and Recommender

## Project Overview
This project combines Exploratory Data Analysis with a production-ready Recommender app centered around the insights that came from the EDA. The EDA utilizes a dataset that was extracted from IGDB.com, a video game database acquired by Twitch, via the IGDB API to provide video game information from 30k+ known video games that contain user ratings amongst a realm of 200k+ total game titles. The notebook explores common trends for games that contain user ratings from IGDB and external critics. 

Here we try to answer the following questions to be tailored towards video game marketing and creation teams: 
1. In which genres does the highest engagement occur?
2. Which theme-genre pairs improve or hurt ratings and engagement?
3. Which gaming platform sees the most success for each genre?
4. Do multi-player games play a factor in getting higher ratings and rating counts than single-player games regardless of platforms, genres, themes, age ratings, and player perspectives?
5. How do game ratings look for different platforms, genres, themes, age ratings and player perspectives and discuss why?

## Table of Contents
- [Project Overview](#project-overview)
- [Summary Of Insights](#summary-of-insights)
- [Recommendations](#recommendations)
- [Assumptions](#assumptions)
- [Demo-Preview](#demo-preview)
- [Installation](#installation)

## Summary of Insights

### Popularity vs Quality
- Adventure is the most common and most engaged genre, sporting over 40% of the entire gaming catalogue and representing 67% of the top 500 games in rating counts. However, it is not included in the top 10 genres organized by average rating, implying that there is saturation in the genre, as well as a generally wide diaspora of player experiences with the genre.
- The Turn‑Based Strategy and Tactical genres rank highest in average rating (~75 for both genres, while all other genres generally float around scores of 70 or below) despite having a smaller presence, altogether appearing in only 7.3% of all games. This suggests that the two genres reach "hidden gem" territory, in which players who enjoy the genres are more likely to enjoy other games from that genre despite its niche.
- Using Avg Rating Count (ARC) vs Avg Rating to classify genres shows a clear split:
  - Popular + High Rated (mainstream winners)
  - Niche + High Rated (hidden gems)
  - Popular + Mid Rated
  - Niche + Low Rated

### Theme & Genre Combinations 
- Themes of Fantasy, Open World, and Drama raise ratings across genres to a steady 70-80 score, suggesting that they are broad crowd-pleasers and most likely to be received well by audiences despite the genre.
- Erotic (and sometimes Educational) themes depress ratings across most genres, *except* for Tactical, implying that these themes are only compatible with games emphasizing decision-making and strategy.
- Adventure is stable across themes, while Pinball, Shooter, Racing show strong theme sensitivity. For example, Pinball/Mystery and Pinball/Thriller shoot the average rating up to scores of 90+, while Pinball/Educational combinations are generally not enjoyed.

### Platforms: Availability vs Engagement
- PC (Windows) leads by title count and engagement, representing 23.23% of all title releases. Their presence is most seen in MOBAs (Multiplayer Online Battle Arena) and RTS (Real-Time Strategy) games, both containing 35% % of their respective genre rating counts.
  - Interestingly, Mac shows an almost equal share of rating counts as PC in the MOBA and RTS genres and is most engaged here (almost 30%), suggesting that Mac users are just as interested in the genres as PC users; higher compatibility for both consoles would thus be advised.
- Nintendo Switch shows diverse engagement overall but comparatively lower in Racing, Shooter, and RTS (<5%), suggesting that Switch has a less marketable niche for these genres. 

### Game Modes and Ratings
- Both (Single + Multi) games rate highest on average; Multiplayer‑only roughly ties/slightly trails; Single‑only is more variable with more low tails.

## Recommendations

## Assumptions 

## Demo Preview

## Installation

![Footer](images-for-readme/gaming_footer.jpg)
