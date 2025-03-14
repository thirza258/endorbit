# Endorbit

## Overview

Endorbit is an e-commerce bot that uses a Flipkart product dataset to recommend products based on your prompt. The bot is built with a tech stack that includes Faiss RAG and OpenAI embeddings for large-scale search and retrieval, and it uses Django REST framework to create its own API. The frontend is developed using React, TypeScript, and Tailwind CSS. The AI capabilities are powered by OpenAI, and the product data is sourced from a Kaggle dataset, which can be found [here](https://www.kaggle.com/datasets/PromptCloudHQ/flipkart-products).

You can also access the chatbot website from [website](https://endorbit.vercel.app/).
## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/thirza258/endorbit.git
    cd Build_your_bot
    ```

2. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Create a `.env` file from the example:
    ```bash
    cp .env.example .env
    ```


## Installation

1. Clone the repository:
    ```bash
    git clone <repository_url>
    cd Build_your_bot
    ```

2. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Create a `.env` file from the example:
    ```bash
    cp .env.example .env
    ```

4. Apply database migrations:
    ```bash
    python manage.py migrate
    ```

5. Import research data:
    ```bash
    python manage.py import_research
    ```

6. Run the development server:
    ```bash
    python manage.py runserver
    ```

## Documentation

For more information, go to `/docs`.
## API Documentation

### Chat API

**Endpoint:** `POST /api/v1/chat/`

**Description:** This API endpoint processes user input and returns a recommended product based on the input.

**Parameters:**

- `input_user` (String): The input message from the user.

**Response:**

- `response` (String): The recommended product based on the user's input.

**Request Example:**

```json
{
    "input_user": "I need a new phone"
}
```

**Success Response Example:**

```json
- HTTP/1.1 200 OK
{
    "status": 200,
    "message": "Success",
    "data": {
        "response": "Here are some recommended products",
        "products": [ {
            "product_name": "Samsung Galaxy M31",
            "product_price": "₹16,499",
            "product_rating": "4.3",
            "product_url": "https://www.flipkart.com/samsung-galaxy-m31-space-black-64-gb",
            "description": "Samsung Galaxy M31 (Space Black, 64 GB)"
            }
        ]
    }
}
```

## Usage

Endorbit will recommend products based on your input prompt using the Flipkart product dataset.
