GreenFund AI API Documentation

Project Name: GreenFund: AI-Driven Climate-Smart Farming

Purpose: This document details the implementation, data flow, and underlying prompt strategies for the Artificial Intelligence services integrated into the GreenFund platform. The AI layer is designed to transform raw data (weather, soil, activity) into actionable, farm-specific advice aligned with climate action and sustainability goals.

Architecture: All AI functions are managed by the FastAPI Backend. The frontend application consumes these services via standard REST endpoints.

I. AI Service Implementation Details

Component

Technology

Role

LLM Engine

OpenAI (GPT-4o, GPT-3.5)

Generative reasoning and advice creation.

Vision Model

OpenAI Vision

Multi-modal analysis of soil images for initial parameter estimation.

API Integration

Python requests library

Secured API calls from the FastAPI backend to OpenAI.

Output Format

JSON Schema

LLM responses are constrained using Pydantic schemas to ensure reliable, structured data output (e.g., lists of crops, risk objects).

II. AI Climate Action Guidance

This suite of endpoints provides predictive and prescriptive guidance tailored to the farm's immediate climatic and operational context.

A. Predictive Pest & Disease Alerts

Endpoint: /api/climate-actions/alerts/{farm_id}

Parameter

Type

Description

farm_id

Integer

The target farm ID.

Logic & Prompt Strategy:

Data Ingestion: Backend fetches the farm's current crop type and the 7-day local weather forecast (temperature, humidity, precipitation).

Risk Assessment (Python Logic): Simple Python logic performs initial anomaly detection (e.g., identifying three consecutive days of high humidity or sudden temperature drops).

LLM Call: The summarized risk factors are injected into the following System Prompt:

SYSTEM INSTRUCTION: "You are 'GreenFund Predict', a pre-emptive agricultural risk advisor. Based on the data provided, identify the most likely pest or disease risk for the specified crop in the next 7 days. Your output must be in a highly structured JSON format."

USER QUERY: "The farm has [Crop Name]. Recent analysis shows: [List of Risk Factors, e.g., '3 days of >85% humidity']. What is the top risk, its severity (Low/Medium/High), and the specific pre-emptive advice for the farmer?"

B. Carbon Sequestration Guidance

Endpoint: /api/climate-actions/carbon-guidance/{farm_id}

Parameter

Type

Description

farm_id

Integer

The target farm ID.

Logic & Prompt Strategy:

Data Ingestion: Backend gathers farm details (size, crop) and the historical log of Farm Activity (e.g., recent tilling, fertilizer use).

LLM Call: The AI is tasked with suggesting concrete behavioral changes to meet climate goals.

SYSTEM INSTRUCTION: "You are 'GreenFund Carbon Analyst'. Your goal is to suggest sustainable farming practices common in East Africa that actively increase soil carbon sequestration and reduce overall emissions. Provide three distinct, immediate actions."

USER QUERY: "Given the farm is [Size] acres, currently growing [Crop], and the last activity was [Activity Type], provide 3 high-impact, actionable steps to increase carbon sequestration. For each action, estimate the relative effort and potential CO2e benefit."

C. Water Management Guidance

Endpoint: /api/climate-actions/water-management/{farm_id}

Parameter

Type

Description

farm_id

Integer

The target farm ID.

Logic & Prompt Strategy:

Data Ingestion: Backend gathers farm location, current crop, soil type (from latest report), and recent rainfall data.

LLM Call: The AI determines optimal irrigation timing and volume to minimize water waste.

SYSTEM INSTRUCTION: "You are 'GreenFund Water Advisor'. Your role is to provide precise, water-saving irrigation advice for the specified crop based on the latest climate data."

USER QUERY: "The farm is located at [Location], growing [Crop], and the soil is [Soil Type]. Recent rainfall has been [Amount]. Advise the farmer on the optimal time and volume for irrigation this week to conserve water while maintaining yield."

III. Multi-Modal Soil Analysis

This service accepts both structured lab data and unstructured image data to provide comprehensive crop recommendations.

Endpoint: /api/soil/manual (Structured Data Analysis)

Logic & Prompt Strategy:

LLM is presented with the explicit pH, Nitrogen, Phosphorus, and Potassium values.

Prompt Focus: “Given these exact soil parameters (pH: X, N: Y, P: Z, K: A) and the geographical region (East Africa), recommend 3 highly suitable crops and provide detailed, actionable fertilization recommendations.”

Endpoint: /api/soil/upload_soil_image/{farm_id} (Multi-Modal Vision Analysis)

Logic & Prompt Strategy:

Input: Base64-encoded image data and the user's prompt.

Process: The image and the prompt are sent to the OpenAI Vision model.

Prompt Focus: “Analyze the provided image of the soil sample. Based on visual cues (texture, color, visible organic matter), estimate the soil's pH range, relative Nitrogen, and Phosphorous levels. Use these estimations to suggest a preliminary crop type.”

Endpoint: /api/soil/suggestions/summary (AI-Derived Summary)

Logic & Prompt Strategy:

Process: This endpoint reads and aggregates suggested_crops from all recent AI-generated soil reports across the user's farms to provide a unified overview on the dashboard.

IV. General Chatbot Interface

Endpoint: /api/chatbot/ask

Parameter

Type

Description



message

String

The user's query.



Logic & Prompt Strategy:

System Prompt: "You are 'GreenFund Assistant', an expert agricultural advisor specializing in sustainable farming practices for East Africa. Maintain a professional, encouraging tone, and keep answers concise and focused on practical, climate-smart solutions."

Process: Provides real-time conversational assistance to the farmer without relying on farm-specific data.
