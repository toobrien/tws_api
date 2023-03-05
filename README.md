A basic implementation of the TWS client for futures and futures strategies.

`fclient` is the client. A few basic examples are implemented, demonstrating the usage.

Requests to `fclient` public methods generally involve instrument IDs, which are tuples in the format:

( `symbol`, `exchange`, `type`, `leg0`, ..., `legN` )

Where `type` is one of:

- `single`: a single contract
- `rcal`:   reverse calendar (+1, -1)
- `fly`:    butterfly        (+1, -2, +1)
- `custom`: arbitrary spread
- `inter`:  intercommodity spread

For `single` and the other standard spreads, the legs are `MYY` format, e.g. J23 for April, 2023.

For `custom` and `inter`, the legs also require side and ratio, separated by a colon from the standard leg representation,  e.g.: `+1:J23` or `-2:K24` and so on.

I intend to implement public functions for:

- L1 streaming data (complete)
- L2 data (partially complete)
- Limit and market order management (not started)
