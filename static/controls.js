if (!window.current_level) {
    window.current_level = "1";
}
if (!AFRAME.utils.device.checkHeadsetConnected() || AFRAME.utils.device.isMobile()) {
    console.log("loading gear controls")
    var gear_html = '<a-entity id="gear-controls-switch">\
                              <a-entity id="cursor" camera universal-controls position="0 1.25 0">\
                                <a-entity position="0 0 -3" scale="0.3 0.3 0.3" geometry="primitive: ring; radiusOuter: 0.30;\
                                      radiusInner: 0.20;" material="color: #3f43ad; shader: flat" cursor="maxDistance: 100;">\
                                  <a-animation begin="click" easing="ease-in" attribute="scale" fill="backwards" from="0.1 0.1 0.1" to="0.5 0.5 0.5" dur="150"></a-animation>\
                                  <a-animation begin="fusing" easing="ease-in" attribute="scale" fill="forwards" from="0.5 0.5 0.t" to="0.1 0.1 0.1" dur="1500"></a-animation>\
                                </a-entity>\
                              </a-entity>\
                            </a-entity>'
    $("#user").append(gear_html) // either desktop or mobile
    console.log("finished loading gear controls")
}
if (!AFRAME.utils.device.isMobile() && AFRAME.utils.device.checkHeadsetConnected()) {
    $("#user").append('<a-camera id="vive_cam"></a-camera>')
    console.log("loading vive controls")
    var vive_html = '<a-entity id="vive-controls-switch">\
                          <a-entity vive-controls="hand: left"></a-entity>\
                          <a-entity vive-controls="hand: right" vive-cursor></a-entity>\
                        </a-entity>'
    $("#user").append(vive_html) // if oculus rift or vive
}