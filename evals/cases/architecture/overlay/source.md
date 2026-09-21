# Retry backoff decision

Choose among the shipped fixed pause, a capped growing backoff, and a lock-file handshake with the program holding the report open. Weight recovery 5, operability 3, and cost 2. The chosen option must survive a report file held open for several seconds without adding a service, a configuration surface, or a dependency.
