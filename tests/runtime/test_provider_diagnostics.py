"""Safe transport error classes using mocked HTTP; no real requests."""
import ssl,unittest
from unittest.mock import patch,MagicMock
from packages.capture.openai_transport import http_post
from packages.domain.source_event import ContractError
from packages.operations.local import safe_code
class ProviderDiagnosticTests(unittest.TestCase):
 def test_timeout_tls_and_json_are_distinct_without_error_text(self):
  cases=[(TimeoutError('private-body'),'provider_timeout_unknown'),(ssl.SSLError('private-body'),'provider_tls_unknown'),(None,'provider_json_invalid')]
  for failure,code in cases:
   with self.subTest(code=code),patch('packages.capture.openai_transport.http.client.HTTPSConnection') as constructor:
    connection=constructor.return_value
    if failure is not None:connection.getresponse.side_effect=failure
    else:
     response=connection.getresponse.return_value;response.status=200;response.read.return_value=b'{bad json}'
    with self.assertRaises(ContractError) as caught:http_post('/v1/responses',{},'fake-private-key')
    self.assertEqual(caught.exception.code,code);self.assertEqual(safe_code(code),code)
    self.assertEqual(constructor.call_args.kwargs['timeout'],120)
    self.assertNotIn('private-body',str(caught.exception));connection.close.assert_called_once()
if __name__=='__main__':unittest.main()
