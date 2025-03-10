# %%
# Repos and Workspaces

# %%
from cascade.repos import Repo

demo_repo = Repo("demo_repo")
demo_modelline = demo_repo.add_line(line_type="model")
demo_dataline = demo_repo.add_line(line_type="data")

# %%

from cascade.workspaces import Workspace

ws = Workspace("workspace")
rp = ws.add_repo("repo")
ln = rp.add_line("line", line_type="model")

model = ln.create_model()
ln.save(model, only_meta=True)
