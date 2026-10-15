"""Check the shared contract used by local and Vercel HTTP adapters."""
import unittest
from src.service import response_for, model_bundle
from api.model import handler as ModelHandler
from api.run import handler as RunHandler
from api.vision import handler as VisionHandler

class APITests(unittest.TestCase):
    def test_model_is_fitted_and_reused(self):
        first = model_bundle()
        self.assertIs(first, model_bundle())
        self.assertEqual(len(first[0].estimators_), 60)
        status, metrics = response_for('model', {})
        self.assertEqual(status, 200)
        self.assertLess(metrics['mae'], metrics['persistence_mae'])

    def test_invalid_requests(self):
        for query in ({'seed':['-1']}, {'seed':['abc']}, {'seed':['']}, {'scenario':['missing']}):
            self.assertEqual(response_for('run', query)[0], 400)
        for value in ('1,2', '1,2,3,-4', '', '1,2,3,10001'):
            self.assertEqual(response_for('vision', {'q':[value]})[0], 400)
        self.assertEqual(response_for('missing', {})[0], 404)

    def test_run_and_vision_contract(self):
        status, result = response_for('run', {'scenario':['rush'], 'seed':['42']})
        self.assertEqual(status, 200)
        self.assertEqual(result['smart']['metrics']['served'], 411)
        self.assertEqual(result['smart']['metrics']['delay_per_arrival'], 54.97)
        status, frame = response_for('vision', {'q':['1,2,3,4']})
        self.assertEqual(status, 200)
        self.assertEqual(frame['counts'], [1,2,3,4])
        self.assertTrue(frame['image'].startswith('data:image/png;base64,'))

    def test_vercel_routes_use_same_service(self):
        self.assertEqual([ModelHandler.endpoint, RunHandler.endpoint, VisionHandler.endpoint], ['model','run','vision'])

    def test_custom_prediction_uses_the_fitted_forest(self):
        for counts in ([1,1,1],[6,6,6],[6,4,2]):
            status,result=response_for('predict', {'counts':[','.join(map(str,counts))]})
            self.assertEqual(status,200)
            expected=float(model_bundle()[0].predict([counts])[0])
            self.assertAlmostEqual(result['prediction'],expected,places=3)
            self.assertEqual(result['inputs'],counts)
            self.assertEqual(result['n_estimators'],60)
            self.assertFalse(result['outside_training_range'])
    def test_custom_prediction_validates_counts(self):
        for value in ('','1,2','1,2,3,4','1.5,2,3','-1,2,3','101,2,3','abc,2,3','nan,2,3'):
            self.assertEqual(response_for('predict', {'counts':[value]})[0],400)
    def test_custom_prediction_flags_unusual_inputs(self):
        status,result=response_for('predict', {'counts':['100,100,100']})
        self.assertEqual(status,200)
        self.assertTrue(result['outside_training_range'])
        self.assertGreaterEqual(result['prediction'],0)
