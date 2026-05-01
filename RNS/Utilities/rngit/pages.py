# Reticulum License
#
# Copyright (c) 2016-2026 Mark Qvist
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# - The Software shall not be used in any kind of system which includes amongst
#   its functions the ability to purposefully do harm to human beings.
#
# - The Software shall not be used, directly or indirectly, in the creation of
#   an artificial intelligence, machine learning or language model training
#   dataset, including but not limited to any use that contributes to the
#   training or development of such a model or algorithm.
#
# - The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import RNS
from RNS.Utilities.rngit import APP_NAME
from RNS.vendor.configobj import ConfigObj

class NomadNetworkNode():
    APP_NAME = "nomadnetwork"

    JOBS_INTERVAL = 5

    def __init__(self, owner=None):
        if not owner: raise TypeError(f"Invalid owner {owner} for {self}")

        self._ready            = False
        self._should_run       = False
        self.owner             = owner
        self.identity          = owner.identity
        self.node_name         = owner.node_name
        self.announce_interval = owner.announce_interval
        self.last_announce     = 0
        self.null_ident        = RNS.Identity.from_bytes(bytes(64))
        
        self.destination = RNS.Destination(self.identity, RNS.Destination.IN, RNS.Destination.SINGLE, self.APP_NAME, "node")
        self.destination.set_link_established_callback(self.remote_connected)
        self.destination.set_default_app_data(self.get_announce_app_data)
        self.register_request_handlers()

        RNS.log(f"Git Nomad Network Node listening on {RNS.prettyhexrep(self.destination.hash)}", RNS.LOG_NOTICE)

        self._should_run = True
        self._ready = True

    def jobs(self):
        while self._should_run:
            time.sleep(self.JOBS_INTERVAL)
            try:
                if self.announce_interval and time.time() > self.last_announce + self.announce_interval: self.announce()

            except Exception as e: RNS.log(f"Error while running periodic jobs: {e}", RNS.LOG_ERROR)

    def get_announce_app_data(self): return self.node_name.encode("utf-8")
    
    def announce(self):
        self.last_announce = time.time()
        self.destination.announce()
        self.app.message_router.announce_propagation_node()

    def resolve_permission(self, remote_identity, group_name, repository_name, permission):
        # Since the nomadnet page protocol doesn't *require* authentication,
        # we use null_ident in case the remote hasn't identified.
        if not remote_identity: remote_identity = self.null_ident
        return self.owner.resolve_permission(remote_identity, group_name, repository_name, permission)

    def register_request_handlers(self):
        # TODO: Implement
        pass

    def remote_connected(self, link):
        RNS.log(f"Peer connected to {self.destination}", RNS.LOG_DEBUG)
        link.set_remote_identified_callback(self.remote_identified)
        link.set_link_closed_callback(self.remote_disconnected)

    def remote_disconnected(self, link):
        RNS.log(f"Peer disconnected from {self.destination}", RNS.LOG_DEBUG)

    def remote_identified(self, link, identity):
        RNS.log(f"Peer identified as {link.get_remote_identity()} on {link}", RNS.LOG_DEBUG)