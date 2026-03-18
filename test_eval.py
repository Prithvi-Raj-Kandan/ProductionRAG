import eval
try:
    print(eval.evaluate_pipeline())
except Exception as e:
    import traceback
    traceback.print_exc()
