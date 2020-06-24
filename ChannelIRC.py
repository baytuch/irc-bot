#!/usr/bin/python
# -*- coding: UTF-8 -*-

import asyncore
import socket


class ChannelIRC(asyncore.dispatcher):

  nick = ''
  buffer_read = ''
  buffer_write = ''
  login_n = 0

  def __init__(self, host, port, nick):
    self.nick = nick
    asyncore.dispatcher.__init__(self)
    self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
    self.connect((host, port))
    asyncore.loop()

  def handle_connect(self):
    print('connect')

  def handle_error(self):
    print('error')

  def handle_close(self):
    print('close')
    self.close()

  def readable(self):
    while True:
      recv_line = self.pull_buffer_read()
      if (recv_line != ''):
        print(self.message_filter(recv_line))
        #print(recv_line)
        self.processor(False, recv_line)
      else:
        break
    return True

  def handle_read(self):
    self.buffer_read += self.recv(8192)

  def writable(self):
    res = False
    writable_len = len(self.buffer_write)
    if (writable_len > 0):
      res = True
    else:
      res = self.processor(True)
    return res

  def handle_write(self):
    print('write')
    sent = self.send(self.buffer_write)
    self.buffer_write = self.buffer_write[sent:]

  def push_buffer_write(self, data):
    self.buffer_write = data + '\r\n'
    print('push to buffer_write: ' + data)

  def pull_buffer_read(self):
    end_sub = '\r\n'
    res = ''
    end_sub_pos = self.buffer_read.find(end_sub)
    if (end_sub_pos != -1):
      res = self.buffer_read[0:end_sub_pos]
      self.buffer_read = self.buffer_read[end_sub_pos + len(end_sub):]
    return res

  def message_filter(self, mess_raw):
    mess_raw = mess_raw.decode('utf-8')
    mess = ''
    subs = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g',
            'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x',
            'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
            'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'а', 'б', 'в', 'г', 'ґ', 'д',
            'е', 'ё', 'ж', 'з', 'и', 'і', 'ї', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т',
            'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я', 'А', 'Б', 'В', 'Г',
            'Ґ', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И', 'І', 'Ї', 'Й', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Р',
            'С', 'Т', 'У', 'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ъ', 'Ы', 'Ь', 'Э', 'Ю', 'Я', '{', '}',
            ']', '[', ')', '(', '~', ':', '>', '<', '"', '/', ',', '.', '!', '?', ' ', '-', '=',
            '#', '*', '@', '_', '%', '%', '&', '+']
    for sub_target in mess_raw:
      for sub in subs:
        if (sub_target == sub.decode('utf-8')):
          mess += sub_target
          break
    return mess

  def message_parser(self, mess):
    sub_sep = ':'
    sub_excl = '!'
    sub_email = '@'
    sub_space = ' '
    res = {'prefix': {'servername': '',
                      'nick': '',
                      'user': '',
                      'host': ''},
           'command': '',
           'params': [],
           'status': False}
    err = False
    servername = ''
    nick = ''
    user = ''
    host = ''
    command = ''
    params = []
    if (mess[0] == sub_sep and mess[1] != sub_space):
      sub_space_pos = mess.find(sub_space)
      if (sub_space_pos != -1 and sub_space_pos > 1):
        prefix_raw = mess[0:sub_space_pos]
        mess = mess[sub_space_pos + len(sub_space):]
        host_start = prefix_raw.rfind(sub_email)
        if (host_start != -1):
          host = prefix_raw[host_start + 1:]
          if (len(host) == 0):
            err = True
          else:
            prefix_raw = prefix_raw[0:host_start]
        user_start = prefix_raw.rfind(sub_excl)
        if (user_start != -1 and not err):
          user = prefix_raw[user_start + 1:]
          if (len(user) == 0):
            err = True
          else:
            prefix_raw = prefix_raw[0:user_start]
        if (not err):
          if (user != ''):
            nick = prefix_raw[1:]
          else:
            servername = prefix_raw[1:]
      else:
        err = True
    if (not err):
      comm_end = mess.find(sub_space)
      if (comm_end != -1 and comm_end > 1):
        command = mess[0:comm_end]
        if (len(command) == 0):
          err = True
        else:
          mess = mess[comm_end + 1:]
      else:
        err = True
    if (not err):
      comb_param = ''
      simple_params = []
      last_param_start = mess.find(sub_sep)
      if (last_param_start != -1):
        comb_param = mess[last_param_start + 1:]
        mess = mess[0:last_param_start]
        if (last_param_start > 0):
          mess = mess[0:last_param_start - 1]
      if (last_param_start > 0):
        simple_params = mess.split(sub_space)
        for simple_param in simple_params:
          if (simple_param == ''):
            err = True
            break
      if (not err):
        params.extend(simple_params)
        params.append(comb_param)
    if (not err):
      res['prefix']['servername'] = servername
      res['prefix']['nick'] = nick
      res['prefix']['user'] = user
      res['prefix']['host'] = host
      res['command'] = command
      res['params'] = params
      res['status'] = True
    #print(res)
    return res

  def processor(self, mode, data = ''):
    res = False
    if (mode):
      if (self.login_n == 0):
        self.push_buffer_write('NICK ' + self.nick)
        self.login_n += 1
        res = True
      elif (self.login_n == 1):
        self.push_buffer_write('USER  ' + self.nick + ' 8 *  : ' + self.nick)
        self.login_n += 1
        res = True
      elif (self.login_n == 2):
        self.push_buffer_write('JOIN #dev')
        self.login_n += 1
        res = True
      elif (self.login_n == 3):
        print('ok')
    else:
      pass
      self.message_parser(data)
    return res

