
# Run: PYTHONPATH=src python3 test/test_code_quality.py

from metrics.code_quality import CodeQuality


def test_code_quality():
    from parsing.url_base import Codebase

    test_repos = [
        "https://github.com/huggingface/transformers.git",
        "https://github.com/openai/whisper.git",
        "https://github.com/microsoft/DialoGPT.git",
        "https://github.com/pytorch/pytorch.git",
        "https://github.com/tensorflow/tensorflow.git",
        "https://github.com/scikit-learn/scikit-learn.git",
        "https://github.com/requests/requests.git",
        "https://github.com/pallets/flask.git",
        "https://github.com/psf/black.git",
        "https://github.com/huggingface/datasets.git",
        "https://github.com/gradio-app/gradio.git",
        "https://github.com/numpy/numpy.git",
        "https://github.com/pandas-dev/pandas.git",
        "https://github.com/matplotlib/matplotlib.git",
        "https://github.com/scipy/scipy.git",
        "https://github.com/sympy/sympy.git",
        "https://github.com/django/django.git",
        "https://github.com/fastapi/fastapi.git",
        "https://github.com/getsentry/sentry.git",
        "https://github.com/celery/celery.git",
        "https://github.com/redis/redis-py.git",
        "https://github.com/sqlalchemy/sqlalchemy.git",
        "https://github.com/sphinx-doc/sphinx.git",
        "https://github.com/pytest-dev/pytest.git",
        "https://github.com/docker/docker-py.git",
        "https://github.com/kubernetes-client/python.git",
        "https://github.com/ansible/ansible.git",
        "https://github.com/saltstack/salt.git",
        "https://github.com/fabric/fabric.git",
        "https://github.com/spyder-ide/spyder.git",
        "https://github.com/ipython/ipython.git",
        "https://github.com/jupyter/notebook.git",
        "https://github.com/plotly/plotly.py.git",
        "https://github.com/bokeh/bokeh.git",
        "https://github.com/altair-viz/altair.git",
        "https://github.com/streamlit/streamlit.git",
        "https://github.com/dagster-io/dagster.git",
        "https://github.com/apache/airflow.git",
        "https://github.com/dask/dask.git",
        "https://github.com/ray-project/ray.git",
        "https://github.com/mlflow/mlflow.git",
        "https://github.com/wandb/wandb.git",
        "https://github.com/optuna/optuna.git",
        "https://github.com/Lightning-AI/lightning.git",
        "https://github.com/open-mmlab/mmdetection.git",
        "https://github.com/facebookresearch/detectron2.git",
        "https://github.com/ultralytics/yolov5.git",
        "https://github.com/ageitgey/face_recognition.git",
        "https://github.com/commaai/openpilot.git",
        "https://github.com/deepfakes/faceswap.git",
        "https://github.com/nltk/nltk.git",
        "https://github.com/explosion/spaCy.git",
        "https://github.com/RasaHQ/rasa.git",
        "https://github.com/huggingface/tokenizers.git",
        "https://github.com/pytorch/vision.git",
        "https://github.com/pytorch/audio.git",
        "https://github.com/torchvision/torchvision.git",
        "https://github.com/keras-team/keras.git",
        "https://github.com/tensorflow/models.git",
        "https://github.com/tensorflow/addons.git",
        "https://github.com/donnemartin/system-design-primer.git",
        "https://github.com/TheAlgorithms/Python.git",
        "https://github.com/karpathy/nanoGPT.git",
        "https://github.com/scrapy/scrapy.git",
        "https://github.com/home-assistant/core.git",
        "https://github.com/ytdl-org/youtube-dl.git"
    ]

    print("Testing Code Quality Analyzer")
    print("=" * 50)

    for repo_url in test_repos:
        print(f"\nAnalyzing: {repo_url}")
        try:
            asset = Codebase(repo_url)
            analyzer = CodeQuality(asset)
            score = analyzer.calculate()

            print(f"  Code Quality Score: {score:.3f}")
            print(f"  Latency: {analyzer.latency}ms")
            if hasattr(analyzer, 'function_length_score'):
                print(f"  Function Length Score: {analyzer.function_length_score:.3f}")
                print(f"  Style Score: {analyzer.style_score:.3f}")
                print(f"  Recency Score: {analyzer.recency_score:.3f}")
                print(f"  Total Functions: {analyzer.total_functions}")
                print(f"  Style Violations: {analyzer.style_violations}")
                print(f"  Days Since Last Commit: {analyzer.days_since_last_commit}")

        except Exception as e:
            print(f"  Error: {e}")


if __name__ == "__main__":
    test_code_quality()