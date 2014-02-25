from __future__ import print_function, division

class Pipeline(object):
    """
    A data processing pipeline for processing power data.  Operates at
    the "Meter" layer.  The basic motivation is that we want to be 
    able to do a sequence of processing steps on a chunk
    while that chunk is in memory.
    
    SOURCE -> LOADER/SPLITTER -> NODE_1 -> ... -> NODE_N
    
    A pipeline consists of one loader/splitter
    node which loads and, if necessary, splits the data into chunks;
    if there are K chunks then the pipeline runs K times; and on each
    iteration the output from the loader/splitter is a single DataFrame
    (with metatdata).
    
    The Loader contains a Source object which defines how to pull
    data from the physical data store (disk / network / device).
    
    After the loader/splitter are an arbitrary number of "nodes"
    which process data in sequence or export the data to disk.
    
    Each processing node has a set of preconditions (e.g. gaps must be
    filled) and a set of postconditions (e.g. gaps will have been
    filled).  This allows us to check that a particular pipeline is
    viable (i.e. that, for every node, the node's preconditions are
    satisfied by an upstream node or by the source).
    
    During a single cycle of the pipeline, results from each
    stats node are stored in the `dataframe.results` dict.  At the end
    of each pipeline cycle, the contents of dataframe.results 
    are combined and the aggregate results are stored in the pipeline.
    
    IDEAS FOR THE FUTURE???:
    Pipelines could be saved/loaded from disk.
    
    If the pipeline was represented by a directed acyclic
    graphical model (DAG) then:
      pipeline could fork into multiple parallel
      pipelines.  Data and metadata would be copied to each fork and
      each sub-pipeline would be run as a separate process (after
      checking requirements for each subpipeline as the start).
    
      Pipelines could be rendered
      graphically.  In the future it would be nice to have a full
      graphical UI (like Node-RED).
    
    Attributes
    ----------
    nodes : list of Node objects
    loader : Loader
    results : dict of Results objects storing aggregate stats results
    
    Examples
    --------
    
    >>> table_path = 'building1/utility/electric/meter1'
    >>> source = HDFTableSource('ukpd.h5', table_path)
    >>> loader = Loader(source, start="2013-01-01", end="2013-06-01")

    Calculate total energy and save the preprocessed data
    and the energy data back to disk:
    
    >>> nodes = [BookendGapsWithZeros(), 
                 Energy(), 
                 HDFTableExport('meter1_preprocessed.h5', table_path)]
    >>> pipeline = Pipeline(loader, nodes).run()
    >>> energy = pipeline.results['energy']
    >>> print("Energy in Joules =", energy.joules, "and kWh =", energy.kwh)
    
    """
    def __init__(self, loader=None, nodes=None):
        self.loader = loader
        self.nodes = [] if nodes is None else nodes
        self.reset()

    def reset(self):
        self.results = {}
        for node in self.nodes:
            node.reset()
            
    def run(self):
        self.reset()
        # TODO: self.check_preconditions()

        # Run pipeline
        for chunk in self.loader.load_chunks(): # TODO only load required measurements
            processed_chunk = self._run_chunk_through_pipeline(chunk)
            self._update_results(processed_chunk.results)

    def _run_chunk_through_pipeline(self, chunk):
        for node in self.nodes:
            chunk = node.process(chunk)
        return chunk
    
    def _update_results(self, results_for_chunk):
        for statistic, result in results_for_chunk.iteritems():
            try:
                self.results[statistic].update(result)
            except KeyError:
                self.results[statistic] = result
                    
            
