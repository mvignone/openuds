# -*- coding: utf-8 -*-

#
# Copyright (c) 2012 Virtual Cable S.L.
# All rights reserved.
#

'''
@author: Adolfo Gómez, dkmaster at dkmon dot com
'''
from __future__ import unicode_literals

from django.utils.translation import ugettext_noop as _
from uds.core.ui.UserInterface import gui
from uds.core.managers.CryptoManager import CryptoManager
from uds.core import osmanagers
from LinuxOsManager import LinuxOsManager

import logging

logger = logging.getLogger(__name__)


class LinuxRandomPassManager(LinuxOsManager):
    typeName = _('Linux Random Password OS Manager')
    typeType = 'LinRandomPasswordManager'
    typeDescription = _('Os Manager to control linux machines, with user password set randomly.')
    iconFile = 'losmanager.png'

    # Apart form data from linux os manager, we need also domain and credentials
    userAccount = gui.TextField(length=64, label=_('Account'), order=2, tooltip=_('User account to change password'), required=True)
    password = gui.PasswordField(length=64, label=_('Password'), order=3, tooltip=_('Current (template) password of the user account'), required=True)

    # Inherits base "onLogout"
    onLogout = LinuxOsManager.onLogout

    def __init__(self, environment, values):
        super(LinuxRandomPassManager, self).__init__(environment, values)
        if values != None:
            if values['userAccount'] == '':
                raise osmanagers.OSManager.ValidationException(_('Must provide an user account!!!'))
            if values['password'] == '':
                raise osmanagers.OSManager.ValidationException(_('Must provide a password for the account!!!'))
            self._userAccount = values['userAccount']
            self._password = values['password']
        else:
            self._userAccount = ''
            self._password = ""

    def release(self, service):
        super(LinuxRandomPassManager, self).release(service)

    def processUserPassword(self, service, username, password):
        if username == self._userAccount:
            return [username, service.recoverValue('linOsRandomPass')]
        return [username, password]

    def genPassword(self, service):
        import random
        import string
        randomPass = service.recoverValue('linOsRandomPass')
        if randomPass is None:
            randomPass = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))
            service.storeValue('linOsRandomPass', randomPass)
        return randomPass

    def infoVal(self, service):
        return 'rename:{0}\t{1}\t{2}\t{3}'.format(self.getName(service), self._userAccount, self._password, self.genPassword(service))

    def infoValue(self, service):
        return 'rename\r{0}\t{1}\t{2}\t{3}'.format(self.getName(service), self._userAccount, self._password, self.genPassword(service))

    def marshal(self):
        base = super(LinuxRandomPassManager, self).marshal()
        '''
        Serializes the os manager data so we can store it in database
        '''
        return '\t'.join(['v1', self._userAccount, CryptoManager.manager().encrypt(self._password), base.encode('hex')])

    def unmarshal(self, s):
        data = s.split('\t')
        if data[0] == 'v1':
            self._userAccount = data[1]
            self._password = CryptoManager.manager().decrypt(data[2])
            super(LinuxRandomPassManager, self).unmarshal(data[3].decode('hex'))

    def valuesDict(self):
        dic = super(LinuxRandomPassManager, self).valuesDict()
        dic['userAccount'] = self._userAccount
        dic['password'] = self._password
        return dic