/*jslint browser: true, devel: true*/
/*global jQuery, SET_ALERT_CONFIG_URL:false, SET_ALERT_WEIGHT_CONFIG_URL:false, SET_DEVICE_ALERT_URL:false, SET_ROOM_ALERT_URL:false, JSON */

var Bluu = (function ($) {
    "use strict";

    var get_config_data = function (alert_cfg) {
            var data, duration, unit;
            data = {};
            data.device_type_id = alert_cfg.data('device_type_id');
            data.alert_id = alert_cfg.data('alert_id');
            data.text = alert_cfg.find('input.text_input').is(':checked');
            data.email = alert_cfg.find('input.email_input').is(':checked');

            duration = alert_cfg.find('input.duration');
            data.duration = duration ? duration.val() : null;

            unit = alert_cfg.find('select.unit');
            data.unit = unit ? unit.val() : null;

            return data;
        },
        get_weight_config_data = function (alert_cfg) {
            var data, weight;
            data = {};
            data.device_type_id = alert_cfg.data('device_type_id');
            data.alert_id = alert_cfg.data('alert_id');
            data.text = alert_cfg.find('input.text_input').is(':checked');
            data.email = alert_cfg.find('input.email_input').is(':checked');

            weight = alert_cfg.find('input.weight');
            data.weight = weight ? weight.val() : null;

            return data;
        },
        set_device_alert = function (checked, user_id, alert_id, device_id, duration, unit, text, email) {
            if (typeof SET_DEVICE_ALERT_URL !== 'undefined') {
                var data = {
                    'checked': checked,
                    'user': user_id,
                    'alert': alert_id,
                    'device': device_id,
                    'duration': duration,
                    'unit': unit,
                    'text_notification': text,
                    'email_notification': email
                };
                $.ajax({
                    type: "POST",
                    url: SET_DEVICE_ALERT_URL,
                    data: JSON.stringify(data),
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    success: function (data) {
                        console.log(data);
                    },
                    failure: function (errMsg) {
                        alert(errMsg);
                    }
                });
            } else {
                console.log('Error! SET_ALERT_URL is not defined.');
            }
        },
        set_room_alert = function (checked, user_id, alert_id, room_id, duration, unit, text, email) {
            if (typeof SET_ROOM_ALERT_URL !== 'undefined') {
                var data = {
                    'checked': checked,
                    'user': user_id,
                    'alert': alert_id,
                    'room': room_id,
                    'duration': duration,
                    'unit': unit,
                    'text_notification': text,
                    'email_notification': email
                };
                $.ajax({
                    type: "POST",
                    url: SET_ROOM_ALERT_URL,
                    data: JSON.stringify(data),
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    success: function (data) {
                        console.log(data);
                    },
                    failure: function (errMsg) {
                        alert(errMsg);
                    }
                });
            } else {
                console.log('Error! SET_ALERT_URL is not defined.');
            }
        },
        set_alert_config = function (user_id, alert_id, device_type_id, duration, unit, text, email) {
            if (typeof SET_ALERT_CONFIG_URL !== 'undefined') {
                var data = {
                    'user': user_id,
                    'alert': alert_id,
                    'device_type': device_type_id,
                    'duration': duration,
                    'unit': unit,
                    'email_notification': email,
                    'text_notification': text
                };
                $.ajax({
                    type: "POST",
                    url: SET_ALERT_CONFIG_URL,
                    data: JSON.stringify(data),
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    success: function (data) {
                        console.log(data);
                    },
                    failure: function (errMsg) {
                        alert(errMsg);
                    }
                });
            } else {
                console.log('Error! SET_ALERT_CONFIG_URL is not defined.');
            }
        },
        set_alert_weight_config = function (user_id, alert_id, device_type_id, weight, text, email) {
            if (typeof SET_ALERT_WEIGHT_CONFIG_URL !== 'undefined') {
                var data = {
                    'user': user_id,
                    'alert': alert_id,
                    'device_type': device_type_id,
                    'weight': weight,
                    'email_notification': email,
                    'text_notification': text
                };
                $.ajax({
                    type: "POST",
                    url: SET_ALERT_WEIGHT_CONFIG_URL,
                    data: JSON.stringify(data),
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    success: function (data) {
                        console.log(data);
                    },
                    failure: function (errMsg) {
                        alert(errMsg);
                    }
                });
            } else {
                console.log('Error! SET_ALERT_WEIGHT_CONFIG_URL is not defined.');
            }
        };

    return {
        get_config_data: get_config_data,
        get_weight_config_data: get_weight_config_data,
        set_device_alert: set_device_alert,
        set_room_alert: set_room_alert,
        set_alert_config: set_alert_config,
        set_alert_weight_config: set_alert_weight_config
    };

}(jQuery));
