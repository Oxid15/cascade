Viewer
======
:py:class:`cascade.meta.MetaViewer`, :py:class:`cascade.meta.MetricViewer`, :py:class:`cascade.meta.HistoryViewer`, :py:class:`cascade.meta.DiffViewer`

Viewers are an interesting part of Cascade's set of tools. Their purpose is to give a user
the power to analyze their experiments and make sense of all meta that is stored after experiments.

MetaViewer is more high-level way to access meta than MetaHandler, but still abstract. It allows to read all 
meta-data in the folder and every child-folders and display it in the console.

MetricViewer is more specific - it reads `metrics` and `parameters` dicts in meta of models in each line and
build a table, which can be viewed in a variety of ways: it can be printed like pandas.DataFrame or plotted in the
web-view by plotly's Table.

Aside of that, MetricViewer has more general web-based interface. It still revolves around same table,
but provides analytical capabilities - plotting interactive scatterplots of metrics and parameters.

HistoryViewer is also a view around meta-data, but it builds a timeline of each line's progress in respect to
specific metric. It can be used to do manual feature selection and hyper-parameter tuning.

DiffViewer allows to see experiments individually and capture what changed between them to track indiviual changes.
It is useful if you do experiments manually and trying to analyze every step.
