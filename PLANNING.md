# **AI Agent Architecture: PropAI**

This document details the technical specifications and functional roles of the multi-agent system that powers the **PropAI** platform. The system is designed to automate the property marketing cycle, from creative asset generation through to proactive customer relationship management (CRM).

# **1\. Content Creator Agent**

This agent serves as the creative engine that turns technical property data into persuasive marketing copy and compelling visuals.

## **Role / Purpose**

Automatically produce high-quality multimedia marketing material for a range of channels (social media, marketplaces, and digital brochures).

## **Key Responsibilities**

* Analyze property unit specifications to draft ad descriptions using the AIDA *copywriting* technique (*Attention, Interest, Desire, Action*).  
* Generate interior design suggestions or virtual *staging* based on raw unit photos.  
* Optimize keywords (SEO) for property listings so they are easy to find in search engines.  
* Adapt the content's tone of voice to the target demographic (for example: millennials, young families, or investors).
* Create landing page to accept incoming leads from promotion that he/she already post. Link use with short that every agent has unique link. 

## **Tech Stack & Tools**

* **LLM:** GPT 5.6  for descriptive and creative text generation.  
* **Vision/Graphics:** GPT Image 2 API for visual asset generation and *virtual staging*.  
* **Metadata:** Google Vision API for automatic labeling of home features from uploaded photos.

# **2\. Sales & Lead Coordinator Agent**

This agent is the front line of interaction with prospective buyers, making sure every question is answered instantly and every lead is qualified before being handed off to a human agent.

## **Role / Purpose**

Manage real-time communication with prospective buyers and filter leads (*lead scoring*) to improve sales efficiency.

## **Key Responsibilities**

* Respond to common questions about price, location, and amenities 24/7 through a chat interface.  
* Qualify leads by asking strategic questions (budget, payment method, purchase urgency).  
* Store lead contact data in the system database in a structured form.  
* Recommend *follow-up* actions to human property agents based on conversation sentiment.

## **Tech Stack & Tools**

* **Communication:** WhatsApp Business API (via Twilio or MessageBird).  
* **NLP:** LangChain with Retrieval-Augmented Generation (RAG) to answer FAQs based on legal PDF documents and property brochures.  
* **Database:** Pinecone or Weaviate (Vector Database) for semantically relevant property information retrieval.

# **3\. Agency Manager Agent**

This agent acts as the operational brain that monitors business health and coordinates field logistics.

## **Role / Purpose**

Optimize agency operations through marketing performance analytics and physical survey schedule management.

## **Key Responsibilities**

* Monitor ad performance across platforms and recommend marketing budget allocation.  
* Automatically arrange field visits (*property survey*) by syncing calendars between property agents and prospective buyers.  
* Generate automated weekly reports on new lead volume, conversion status, and field agent effectiveness.  
* Send automatic reminders to buyers and agents a few hours before a scheduled survey begins.

## **Tech Stack & Tools**

* **Scheduling:** Google Calendar API for schedule and availability syncing.  
* **Analytics:** Python (Pandas/Scikit-learn) for performance data processing and sales trend prediction.  
* **Workflow:** Langflow for workflow integration across third-party platforms.

# **Integrated Workflow**

| Stage | Responsible Agent | Output |
| :---- | :---- | :---- |
| **Property Onboarding** | Content Creator Agent | Ads, Optimized Photos, Metadata |
| **Buyer Interaction** | Sales & Lead Coordinator | Qualified Lead Data, Chat Logs |
| **Conversion & Survey** | Agency Manager Agent | Calendar Schedules, ROI Report |
