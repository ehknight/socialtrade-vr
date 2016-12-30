$(document).ready(function () {
   AFRAME.registerComponent("move", {
        schema: {
            target: { type: "selector" },
            position: { type: "string" },
            level: { type: "string" }
        },
        init: function () {
            this.el.addEventListener("click", function () {
                $.playSound('/static/button_click');
                cur_scale = this.el.getAttribute("scale")
                console.log(cur_scale)
                console.log(this.el)
                if (cur_scale.x == 1 && cur_scale.y == 2 && cur_scale.z == 7) {
                    var clicked_animation_1 = document.createElement("a-animation");
                    clicked_animation_1.setAttribute("attribute", "scale");
                    clicked_animation_1.setAttribute("from", "1 2 7")
                    clicked_animation_1.setAttribute("to", "1.2 2.4 8.4");
                    clicked_animation_1.setAttribute("dur", "200")
                    clicked_animation_1.setAttribute("repeat", "0");
                    this.el.appendChild(clicked_animation_1)

                    var clicked_animation_2 = document.createElement("a-animation");
                    clicked_animation_2.setAttribute("delay", "200")
                    clicked_animation_2.setAttribute("attribute", "scale");
                    clicked_animation_2.setAttribute("from", "1.2 2.4 8.4");
                    clicked_animation_2.setAttribute("to", "1 2 7");
                    clicked_animation_2.setAttribute("dur", "200")
                    clicked_animation_2.setAttribute("repeat", "0");
                    this.el.appendChild(clicked_animation_2)
                }
                if (window.current_level != this.data.level) {
                    console.log("activated animation")
                    $.playSound("/static/whoosh")
                    console.log(this.data.level)
                    window.current_level = this.data.level
                    var animation = document.createElement("a-animation");
                    animation.setAttribute("attribute", "position");
                    if (this.data.position == "0 0 0") {
                        animation.setAttribute("to", "0 1.25 0");
                    } else {
                        animation.setAttribute("to", this.data.position);
                    }
                    animation.setAttribute("dur", "1000");
                    animation.setAttribute("repeat", "0");
                    this.data.target.appendChild(animation);
                } else {
                    console.log("same animation level")
                }
            }.bind(this));
        }
    });
});