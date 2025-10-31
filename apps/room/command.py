# action: conversation

front = {
    "msg": "How are you?",
    "device_name": "device1",
}
back = {
    "action": "conversation",
    "msg": "How are you?",
    "response": "I am fine, thank you!",
    "device_name": "device1",
}

# action: move

front = {
    "msg": "Move to device2",
    "device_name": "device1",
}
back = {
    "action": "move",
    "to_device_name": "device2",
    "msg": "Move to device2",
    "response": "Moving to device2.",
    "device_name": "device1",
}

# action: animation

front = {
    "msg": "Jump",
    "device_name": "device1",
}
back = {
    "action": "animation",
    "animation_type": "jump",
    "msg": "Jump",
    "response": "now jumping.",
    "device_name": "device1",
}
