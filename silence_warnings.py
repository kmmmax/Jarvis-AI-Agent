import sys
import io

original_stderr = sys.stderr
sys.stderr = io.StringIO()