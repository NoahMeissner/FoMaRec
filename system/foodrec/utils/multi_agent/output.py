# Noah Meissner 09.08.2025

'''
These methods print Model output into the Terminal
'''

def output_user_analyst(analysis_data):
    print(20*'='+'User Analyst'+20*'=')
    print(analysis_data)
    print(40*'=')

def output_search(result):
        print(20*'='+"Searcher"+20*'=')
        for recipe in result:
            print(f"🥇 {recipe['id']}. {recipe['title']}")
            print(f"{recipe['cuisine']}")
            print(f"⏱️ {recipe['cooking_time']} Min")
            print(recipe['ingredients'])
            print(f"{int(recipe['calories'])} kcal")
            print(10*'=')
        print(20*'=')

def output_reflector(is_final, should_continue, feedback):
        print(20*'='+"Reflector"+20*'=')
        print(f"is_final: {is_final}")
        decision = "ACCEPTED" if is_final else "REJECTED"
        print(f"Decision: {decision}")
        print(f"should_continue: {should_continue}")
        print(f"feedback: {feedback}")
        print(20*'=')

def output_manager(thought, action,obersvation, routing, isfinal):
        print("👩‍💼 Manager")
        print(60*"=")
        print(f"💭 THOUGHT: {thought}")
        print(f"Action: {action}")
        print(f"Observation: {obersvation}")
        print(10*'=')
        print(f"Routing: {routing}")
        print(f"is_final: {isfinal}")

def output_item_analyst(results):
        print(20*'='+"Item Analyst"+'='*20)
        explanations = results['explanations']
        for index, expl in enumerate(explanations):
            print(f"Recipe {index}")
            print(f"Explanation: {expl}")
            print(10*"=")

def output_interpreter(result):
         print(20*'='+"Task Interpreter"+20*'=')
         print(f"Interpretation: {result}")