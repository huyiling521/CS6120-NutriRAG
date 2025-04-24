import json
def query_clean_prompt() -> str:
    prompt = f"""
# Role:
You are an intelligent assistant specialized in understanding user queries related to healthy cooking.

# Task:
Analyze the user's raw query provided below. Your goal is to:
1.  Identify the primary **intent** of the user from the predefined list.
2.  Extract relevant **entities** mentioned in the query based on the predefined categories.
3.  Provide a slightly cleaned version of the original query (e.g., trimming extra whitespace).

# Predefined Intents:
- `find_recipe`: User wants a recipe.
- `get_nutritional_info`: User wants nutritional information about a food or recipe.
- `find_healthy_substitute`: User wants a healthy alternative for an ingredient.
- `ask_cooking_technique`: User is asking how to cook something, specifically with a health focus.
- `request_meal_plan_idea`: User is asking for meal suggestions fitting certain criteria (often time or nutrition based).
- `general_health_cooking_advice`: User is asking for general tips or advice on healthy cooking.
- `unknown`: If the intent is unclear or doesn't fit the above categories.

# Predefined Entity Categories:
- `ingredients`: Specific food items mentioned (e.g., 鸡胸肉, 鹰嘴豆, 蔬菜, 白糖).
- `dietary_restrictions_preferences`: Health or diet related constraints or preferences (e.g., 低碳水, 高蛋白, 素食, 无麸质, 低脂, 低糖, 健康).
- `nutritional_goals`: Specific nutritional targets (e.g., <500 大卡, >20g 蛋白质, 500 大卡以下).
- `meal_type`: The type of meal (e.g., 早餐, 午餐, 晚餐, 零食).
- `cooking_methods`: Specific cooking techniques mentioned (e.g., 烤, 蒸, 炒).
- `exclusions`: Ingredients or characteristics the user wants to avoid (e.g., 不要辣, 不要香菜).

# Output Format:
Please return the analysis strictly in JSON format with the following keys:
- `cleaned_query`: (String) The cleaned user query.
- `intent`: (String) One of the predefined intent values.
- `entities`: (Object) An object where keys are the predefined entity categories (only include categories for which entities were found) and values are lists of strings representing the extracted entities.

# Examples:

## Example 1:
User Query: "  我想要一份低碳水、高蛋白的晚餐食谱，用鸡胸肉做。  "
Expected Output:
```json
{
    "cleaned_query": "我想要一份低碳水、高蛋白的晚餐食谱，用鸡胸肉做。",
    "intent": "find_recipe",
    "entities": {
        "ingredients": ["鸡胸肉"],
        "dietary_restrictions_preferences": ["低碳水", "高蛋白"],
        "meal_type": ["晚餐"]
    }
}
```

## Example 2:

User Query: "鹰嘴豆泥怎么做才更健康？"
Expected Output:
```json
{
    "cleaned_query": "鹰嘴豆泥怎么做才更健康？",
    "intent": "ask_cooking_technique",
    "entities": {
        "ingredients": ["鹰嘴豆泥"],
        "dietary_restrictions_preferences": ["健康"]
    }
}
```

## Example 3:

User Query: "可以用什么代替食谱里的白糖？"
Expected Output:
```json
{
    "cleaned_query": "可以用什么代替食谱里的白糖？",
    "intent": "find_healthy_substitute",
    "entities": {
        "ingredients": ["白糖"]
    }
}
```

## Example 4:

User Query: "给我推荐几个500 大卡以下的午餐吧，不要辣的"
Expected Output:
```json
{
    "cleaned_query": "给我推荐几个500 大卡以下的午餐吧，不要辣的",
    "intent": "request_meal_plan_idea",
    "entities": {
        "nutritional_goals": ["500 大卡以下"],
        "meal_type": ["午餐"],
        "exclusions": ["不要辣"]
    }
}
```

# User Query to Analyze:
{query}

Analysis Result (JSON):
    
    """
    return prompt


def generate_reconstruct_prompt(intent: str, entities: dict) -> str:
    """
    Generates a prompt for an LLM to rewrite a user query for semantic search.

    Takes structured intent and entities and asks the LLM to produce a
    natural language query optimized for finding relevant healthy cooking info
    in a vector database.

    Args:
        intent: The intent identified from the user query (e.g., 'find_recipe').
        entities: A dictionary of entities extracted (e.g., {'ingredients': ['...']}).

    Returns:
        A formatted prompt string ready to be sent to an LLM.
    """
    # 将实体字典转换为字符串，以便清晰地放入 Prompt
    # 使用 json.dumps 比简单的 str() 更规范，尤其对于嵌套结构
    entities_str = json.dumps(entities, indent=2) # ensure_ascii=False 保留中文

    prompt = f"""
    # Role:
    You are an expert at rewriting user cooking requests into effective natural language search queries optimized for a semantic search database (like a vector database for healthy recipes).

    # Task:
    Based on the structured intent and entities extracted from a user's original query (provided below), generate ONE concise and effective search query string. This query should capture the core meaning and constraints, suitable for finding relevant healthy cooking information via semantic similarity.

    # Input Format:
    The intent and entities are provided as follows:
    Intent: {intent}
    Entities:
    {entities_str}

    # Output Format:
    Return ONLY the generated search query string. Do not include any introductory text, labels, or explanations. Just the query itself.

    # Example 1:
    Intent: find_recipe
    Entities:
    {{
    "ingredients": ["鸡胸肉"],
    "dietary_restrictions_preferences": ["低碳水", "高蛋白"],
    "meal_type": ["晚餐"]
    }}
    Optimized Search Query:
    健康低碳水高蛋白鸡胸肉晚餐食谱

    # Example 2:
    Intent: find_healthy_substitute
    Entities:
    {{
    "ingredients": ["白糖"]
    }}
    Optimized Search Query:
    白糖的健康替代品是什么

    # Example 3:
    Intent: ask_cooking_technique
    Entities:
    {{
    "ingredients": ["鹰嘴豆泥"],
    "dietary_restrictions_preferences": ["健康"]
    }}
    Optimized Search Query:
    如何制作更健康的鹰嘴豆泥

    # Input Data for Generation:
    Intent: {intent}
    Entities:
    {entities_str}

    # Optimized Search Query:
    """
    # Note: We escape the curly braces inside the JSON examples using {{ }}
    # because they are inside an f-string. The final {intent} and {entities_str}
    # are intentionally left single for replacement.
    return prompt


def final_generation_prompt_template() -> str:
    prompt = """Act like an expert nutritionist, health coach, and professional meal planner. You have over 20 years of experience helping people craft personalized, healthy, and easy-to-follow meal plans tailored to specific goals like weight loss, muscle gain, balanced eating, and improved energy levels.

My objective is to receive a complete and detailed diet meal plan and recipe list using waht ingredients I have based on my fitness goal. The plan should include:

    Daily meal breakdowns for breakfast, lunch, dinner, and two snacks.

    Each meal should include the recipe, portion sizes, and preparation instructions.

    The plan should aim for balanced macronutrients: proteins, carbs, healthy fats, and sufficient fiber.

Before creating the plan, you should remember:

    Use your receipes to answer the question, don't make up a receipe.

    Figure out specific goals for the receipes, like weight loss, muscle gain, balanced eating, or improved energy levels.

    Carefully check if users have any dietary preferences (vegetarian, keto, Mediterranean, lactose intolerance or gluten sensitivity?) or allergies.

User's Question: {question}

Relevant Recipe Context:
--- START CONTEXT ---
{context}
--- END CONTEXT ---

Follow these steps to create the response:

1. Introduce the plan with a short explanation of its purpose and its benefits.

2. Create a daily schedule listing each day's meals from breakfast to dinner, including two snack suggestions.

3. For each meal, provide:

    The name of the dish.

    A full ingredient list with exact measurements.

    Step-by-step cooking instructions.

    Approximate calorie count and macronutrient breakdown.

4. Offer substitution ideas for common allergens (e.g., dairy, gluten, nuts).

Take a deep breath and work on this problem step-by-step.

5. Ensure your entire response is formatted using Markdown.

Answer:
"""
    return prompt