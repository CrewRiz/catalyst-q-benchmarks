# Catalyst-Q SDK QUBO/Max-Cut Campaign

This campaign exercises the public Catalyst-Q SDK QUBO and Max-Cut request builders and records exact reference certificates.
It does not disclose proprietary execution internals.

## Summary

- SDK rows: 2
- Exact reference rows: 2
- Live API execution: enabled

## Results

| Instance | Solver | Status | Objective | Validator |
|---|---|---:|---:|---|
| biqmac_qubo_6_smoke | exact-enumeration-reference | optimal | -4.0 | exact_qubo_certificate |
| biqmac_qubo_6_smoke | catalyst-q-sdk | unknown |  | sdk_request_prepared |
| biqmac_maxcut_6_smoke | exact-enumeration-reference | optimal | 9.0 | exact_maxcut_certificate |
| biqmac_maxcut_6_smoke | catalyst-q-sdk | unknown |  | sdk_request_prepared |
