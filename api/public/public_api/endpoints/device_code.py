# Mycroft Server - Backend
# Copyright (C) 2019 Mycroft AI Inc
# SPDX-License-Identifier: 	AGPL-3.0-or-later
#
# This file is part of the Mycroft Server.
#
# The Mycroft Server is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""Endpoint to generate a pairing code and return it to the device.

The response returned to the device consists of:
    code: A six character string generated from a limited set of characters
        (ACEFHJKLMNPRTUVWXY3479) chosen to be easily distinguished when
        spoken or viewed on a device’s display.

    expiration: An integer representing the number of seconds in a day,
        which is the amount of time until a pairing code expires.

    state: A string generated by the device using uuid4. Used by device to
        identify the pairing session.

    token: A SHA512 hash of a string generated by the API using uuid4.
        Used by the API as a unique identifier for the pairing session.
"""
import hashlib
import json
import random
import uuid
from http import HTTPStatus
from logging import getLogger

from selene.api import PublicEndpoint
from selene.util.cache import DEVICE_PAIRING_CODE_KEY

ONE_DAY = 86400

_log = getLogger(__package__)


class DeviceCodeEndpoint(PublicEndpoint):
    # Avoid using ambiguous characters in the pairing code, like 0 and O, that
    # are hard to distinguish on a device display.
    allowed_characters = "ACEFHJKLMNPRTUVWXY3479"

    def __init__(self):
        super(DeviceCodeEndpoint, self).__init__()

    def get(self):
        """Return a pairing code to the requesting device.

        The pairing process happens in two steps.  First step generates
        pairing code.  Second step uses the pairing code to activate the device.
        The state parameter is used to make sure that the device that is
        """
        response_data = self._build_response()
        return response_data, HTTPStatus.OK

    def _build_response(self):
        """
        Build the response data to return to the device.

        The pairing code generated may already exist for another device. So,
        continue to generate pairing codes until one that does not already
        exist is created.
        """
        response_data = dict(
            state=self.request.args['state'],
            token=self._generate_token(),
            expiration=ONE_DAY
        )
        pairing_code_added = False
        while not pairing_code_added:
            pairing_code = self._generate_pairing_code()
            _log.debug('Generated pairing code ' + pairing_code)
            response_data.update(code=pairing_code)
            pairing_code_added = self.cache.set_if_not_exists_with_expiration(
                DEVICE_PAIRING_CODE_KEY.format(pairing_code=pairing_code),
                value=json.dumps(response_data),
                expiration=ONE_DAY
            )
            log_msg = 'Pairing code {pairing_code} exists, generating new code'
            _log.debug(log_msg.format(pairing_code=pairing_code))

        return response_data

    @staticmethod
    def _generate_token():
        """Generate the token used by this API to identify pairing session"""
        sha512 = hashlib.sha512()
        sha512.update(bytes(str(uuid.uuid4()), 'utf-8'))
        return sha512.hexdigest()

    def _generate_pairing_code(self):
        """Generate the pairing code that will be spoken by the device."""
        return ''.join(random.choice(self.allowed_characters) for _ in range(6))
