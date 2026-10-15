import unittest
import numpy as np
from src.model import train
from src.simulation import arrivals_for,simulate,compare
from src.vision import scene,detect
class ProjectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.model,cls.metrics=train()
    def test_reproducible_arrivals(self):
        np.testing.assert_array_equal(arrivals_for('rush',42,600),arrivals_for('rush',42,600))
    def test_conservation_and_shared_arrivals(self):
        r=compare(self.model,'surge',7)
        for key in ('fixed','smart','reactive'):
            m=r[key]['metrics'];self.assertEqual(m['arrivals'],m['served']+m['remaining']);self.assertEqual(m['arrivals'],r['fixed']['metrics']['arrivals'])
    def test_empty_traffic(self):
        r=simulate(np.zeros((120,4),dtype=int),self.model,True)
        self.assertEqual(r['metrics']['queue_seconds'],0);self.assertEqual(r['metrics']['served'],0)
    def test_cv_counts_from_pixels(self):
        for counts in ([0,0,0,0],[1,4,7,9],[20,2,0,11]):
            boxes,actual=detect(scene(counts));self.assertEqual(actual,[min(9,n) for n in counts]);self.assertEqual(len(boxes),sum(actual))
    def test_transition_has_no_discharge(self):
        a=np.ones((80,4),dtype=int);h=simulate(a)['history']
        # Every two-second sample entirely within a transition must have no additional departures.
        for prev,now in zip(h,h[1:]):
            if prev['amber'] and now['amber']:self.assertEqual(prev['served'],now['served'])
    def test_forecasts_are_finite_and_respond_to_demand(self):
        predictions=self.model.predict([[0,0,0],[1,1,1],[3,3,3],[6,6,6]])
        self.assertTrue(np.all(np.isfinite(predictions)))
        self.assertTrue(np.all(predictions>=0))
        self.assertTrue(np.all(np.diff(predictions)>0))
    def test_controller_passes_only_past_arrivals_to_model(self):
        class RecordingModel:
            def __init__(self): self.inputs=[]
            def predict(self,x):
                self.inputs.append(np.array(x))
                return np.zeros(len(x))
        recorder=RecordingModel()
        arrivals=np.zeros((40,4),dtype=int)
        arrivals[:10,0]=1
        arrivals[10:20,1]=2
        arrivals[20:30,2]=3
        arrivals[30:,3]=4
        simulate(arrivals,recorder,True)
        self.assertEqual(len(recorder.inputs),4)
        np.testing.assert_array_equal(recorder.inputs[0],np.zeros((4,3)))
        np.testing.assert_array_equal(recorder.inputs[3],[[0,0,10],[0,20,0],[30,0,0],[0,0,0]])
    def test_learned_forecast_changes_signal_decisions(self):
        result=compare(self.model,'rush',42)
        smart=[(h['phase'],h['amber']) for h in result['smart']['history']]
        reactive=[(h['phase'],h['amber']) for h in result['reactive']['history']]
        self.assertNotEqual(smart,reactive)
    def test_model_beats_persistence_on_heldout_episodes(self):
        self.assertLess(self.metrics['mae'],self.metrics['persistence_mae'])
if __name__=='__main__': unittest.main()
