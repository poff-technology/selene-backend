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

from dataclasses import dataclass
from datetime import datetime

from selene.data.geography import City, Country, Region, Timezone
from .text_to_speech import TextToSpeech
from .wake_word import WakeWord


@dataclass
class Device(object):
    """Representation of a Device"""
    account_id: str
    city: City
    country: Country
    core_version: str
    enclosure_version: str
    id: str
    name: str
    platform: str
    region: Region
    text_to_speech: TextToSpeech
    timezone: Timezone
    wake_word: WakeWord
    last_contact_ts: datetime = None
    placement: str = None
