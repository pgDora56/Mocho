# yopen

## 必要なLibrary

- websocket-client

## Lobby

接続時に以下のようなID通知が来る

```json
{"type":"selfID","content":2706530918771215}
```

ルームの状態に変更があれば以下のようなメッセージが来る

```json
{
  "type": "rooms",
  "content": [
    {
      "no": 1,
      "numUsers": 6,
      "title": "XXX",
      "hasPassword": true
    },
    {
      "no": 2,
      "numUsers": 0,
      "title": "",
      "hasPassword": false
    },
    {
      "no": 3,
      "numUsers": 0,
      "title": "",
      "hasPassword": false
    },
    {
      "no": 4,
      "numUsers": 0,
      "title": "",
      "hasPassword": false
    },
    {
      "no": 5,
      "numUsers": 0,
      "title": "",
      "hasPassword": false
    },
    {
      "no": 6,
      "numUsers": 0,
      "title": "",
      "hasPassword": false
    },
    {
      "no": 7,
      "numUsers": 0,
      "title": "",
      "hasPassword": false
    },
    {
      "no": 8,
      "numUsers": 0,
      "title": "",
      "hasPassword": false
    },
    {
      "no": 9,
      "numUsers": 0,
      "title": "",
      "hasPassword": false
    },
    {
      "no": 10,
      "numUsers": 0,
      "title": "",
      "hasPassword": false
    },
    {
      "no": 11,
      "numUsers": 0,
      "title": "",
      "hasPassword": false
    },
    {
      "no": 12,
      "numUsers": 0,
      "title": "",
      "hasPassword": false
    },
    {
      "no": 13,
      "numUsers": 0,
      "title": "",
      "hasPassword": false
    },
    {
      "no": 14,
      "numUsers": 0,
      "title": "",
      "hasPassword": false
    },
    {
      "no": 15,
      "numUsers": 0,
      "title": "",
      "hasPassword": false
    },
    {
      "no": 16,
      "numUsers": 0,
      "title": "",
      "hasPassword": false
    },
    {
      "no": 17,
      "numUsers": 0,
      "title": "",
      "hasPassword": false
    },
    {
      "no": 18,
      "numUsers": 0,
      "title": "",
      "hasPassword": false
    },
    {
      "no": 19,
      "numUsers": 0,
      "title": "",
      "hasPassword": false
    },
    {
      "no": 20,
      "numUsers": 0,
      "title": "",
      "hasPassword": false
    },
    {
      "no": 21,
      "numUsers": 0,
      "title": "",
      "hasPassword": false
    },
    {
      "no": 22,
      "numUsers": 0,
      "title": "",
      "hasPassword": false
    },
    {
      "no": 23,
      "numUsers": 0,
      "title": "",
      "hasPassword": false
    },
    {
      "no": 24,
      "numUsers": 0,
      "title": "",
      "hasPassword": false
    }
  ]
}
```

## 入室系

### ルーム作成

```json
{
  "c": "join",
  "a": {
    "name": "a",
    "observer": false,
    "chatAnswer": false,
    "color": {
      "index": 0,
      "custom": "#ffffff"
    },
    "roomNo": 21,
    "first": true,
    "tag": {
      "title": "a",
      "password": "a"
    },
    "scoreBackup": null
  }
}
```

### 入室

```json
{
	"c": "join",
	"a": {
		"name": "ころ",
		"observer": false,
		"chatAnswer": false,
		"color": {
			"index": 0,
			"custom": "#ffffff"
		},
		"roomNo": 21,
		"first": false,
		"tag": {
			"password": "a"
		},
		"scoreBackup": null
	}
}
```

### 退室

```json
{"c":"leave"}
```

## ルーム内オペレーション

###  Player

#### チャット

```json
{"c":"chat","a":"もちょ"}
```

#### 押す

```json
{"c":"push"}
```

#### 司会切替

```json
{"c":"toggle-master"}	
```

#### 観戦切り替え

```json
{"c":"toggle-observer"}
```

### Master

#### 正解

```json
{"c":"correct","a":{"keepRight":false}}	
{"c":"wrong","a":{"keepRight":false}}	
{"c":"through"}
{"c":"reset"}
{"c":"undo"}
{"c":"redo"}
{"c":"clear"}
{"c":"win-top"}
{"c":"clear"}
{"c":"shuffle"}
```

#### スコア変更

##### nomx

```json
{
	"c": "scores",
	"a": {
		"2706530918771215": {
			"point": 0,
			"batsu": 0,
			"lock": 0,
			"compPoint": 0,
			"consCorrect": 0,
			"passSeat": false,
			"riichi": {
				"win": false,
				"lose": false,
				"teamWin": false,
				"teamLose": false
			},
			"win": 0,
			"lose": 0,
			"winTimes": 0
		},
		"6067796729619850": {
			"point": 0,
			"batsu": 1,
			"lock": 0,
			"compPoint": 0,
			"consCorrect": 0,
			"passSeat": false,
			"riichi": {
				"win": false,
				"lose": false,
				"teamWin": false,
				"teamLose": false
			},
			"win": 0,
			"lose": 0,
			"winTimes": 0
		},
		"6112766460846462": {
			"point": 3,
			"batsu": 0,
			"lock": 0,
			"compPoint": 0,
			"consCorrect": 0,
			"passSeat": false,
			"riichi": {
				"win": false,
				"lose": false,
				"teamWin": false,
				"teamLose": false
			},
			"win": 0,
			"lose": 0,
			"winTimes": 0
		}
	}
}
```

#### ルール設定

```json
{
	"c": "rule",
	"a": {
		"right": {
			"num": 1,
			"nextPlayer": false,
			"naidesu": false
		},
		"player": {
			"initPoint": 0,
			"initBatsu": 0,
			"pointCorrect": 1,
			"pointWrong": 0,
			"batsuWrong": 1,
			"lockWrong": 0,
			"specialCorrect": {
				"consBonus": false,
				"passQuiz": false,
				"survival": {
					"active": false,
					"value": -1
				}
			},
			"specialWrong": {
				"updown": false,
				"swedish": false,
				"backstream": false,
				"freeze": false,
				"divide": false,
				"belowLock": false
			},
			"comprehensive": {
				"active": false,
				"calc": "mul",
				"winPoint": {
					"active": true,
					"value": 100,
					"above": true
				}
			},
			"winPlayers": 0,
			"winPoint": {
				"active": true,
				"value": 7,
				"above": true
			},
			"losePoint": {
				"active": false,
				"value": 0,
				"above": false
			},
			"loseBatsu": {
				"active": true,
				"value": 3,
				"above": true
			}
		},
		"team": {
			"active": false,
			"numTeams": 1,
			"shareButton": false,
			"point": "sum",
			"batsu": "sum",
			"shareLock": false,
			"winPlayers": 0,
			"winPoint": {
				"active": true,
				"value": 7,
				"above": true
			},
			"losePoint": {
				"active": false,
				"value": 0,
				"above": false
			},
			"loseBatsu": {
				"active": true,
				"value": 3,
				"above": true
			}
		},
		"board": {
			"active": false,
			"pointCorrect": 1,
			"applyNormal": true
		},
		"other": {
			"timer": {
				"active": false,
				"min": 0,
				"sec": 0
			},
			"showWinTimes": false,
			"winLoseOrder": "point"
		},
		"preset": {
			"loseBatsu": 3,
			"name": "nomx",
			"winPlayers": 0,
			"winPoint": 7
		},
		"showScore": true
	}
}
```

##### フリー

```json
{
	"c": "rule",
	"a": {
		"right": {
			"num": 1,
			"nextPlayer": false,
			"naidesu": false
		},
		"player": {
			"initPoint": 0,
			"initBatsu": 0,
			"pointCorrect": 1,
			"pointWrong": 0,
			"batsuWrong": 1,
			"lockWrong": 0,
			"winPlayers": 0,
			"winPoint": {
				"active": false,
				"value": 7,
				"above": true
			},
			"losePoint": {
				"active": false,
				"value": 0,
				"above": false
			},
			"loseBatsu": {
				"active": false,
				"value": 3,
				"above": true
			},
			"specialCorrect": {
				"consBonus": false,
				"passQuiz": false,
				"survival": {
					"active": false,
					"value": -1
				}
			},
			"specialWrong": {
				"updown": false,
				"swedish": false,
				"backstream": false,
				"freeze": false,
				"divide": false,
				"belowLock": false
			},
			"comprehensive": {
				"active": false,
				"calc": "mul",
				"winPoint": {
					"active": true,
					"value": 100,
					"above": true
				}
			}
		},
		"team": {
			"active": false,
			"numTeams": 1,
			"shareButton": false,
			"point": "sum",
			"batsu": "sum",
			"shareLock": false,
			"winPlayers": 0,
			"winPoint": {
				"active": true,
				"value": 7,
				"above": true
			},
			"losePoint": {
				"active": false,
				"value": 0,
				"above": false
			},
			"loseBatsu": {
				"active": true,
				"value": 3,
				"above": true
			}
		},
		"board": {
			"active": false,
			"pointCorrect": 1,
			"applyNormal": true
		},
		"other": {
			"timer": {
				"active": false,
				"min": 0,
				"sec": 0
			},
			"showWinTimes": false,
			"winLoseOrder": "point"
		},
		"preset": {
			"name": "free",
			"lockWrong": 0
		},
		"showScore": true
	}
}

{"c":"rule","a":{"right":{"num":1,"nextPlayer":false,"naidesu":false},"player":{"initPoint":0,"initBatsu":0,"pointCorrect":1,"pointWrong":0,"batsuWrong":1,"lockWrong":0,"winPlayers":0,"winPoint":{"active":false,"value":7,"above":true},"losePoint":{"active":false,"value":0,"above":false},"loseBatsu":{"active":false,"value":3,"above":true},"specialCorrect":{"consBonus":false,"passQuiz":false,"survival":{"active":false,"value":-1}},"specialWrong":{"updown":false,"swedish":false,"backstream":false,"freeze":false,"divide":false,"belowLock":false},"comprehensive":{"active":false,"calc":"mul","winPoint":{"active":true,"value":100,"above":true}}},"team":{"active":false,"numTeams":1,"shareButton":false,"point":"sum","batsu":"sum","shareLock":false,"winPlayers":0,"winPoint":{"active":true,"value":7,"above":true},"losePoint":{"active":false,"value":0,"above":false},"loseBatsu":{"active":true,"value":3,"above":true}},"board":{"active":false,"pointCorrect":1,"applyNormal":true},"other":{"timer":{"active":false,"min":0,"sec":0},"showWinTimes":false,"winLoseOrder":"point"},"preset":{"name":"free","lockWrong":0},"showScore":true}}
```