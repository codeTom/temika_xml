from TemikaXML import TemikaXML
import numpy as np

class EasyTemikaXML(TemikaXML):
    """
    A collection of helpers extending the basic TemikaXML
    """

    def take_image(self):
        """
        Take a short (0.1s) recording    
   
        TODO: make this a single frame
        """
        self.record_start()
        self.sleep(0.1)
        self.record_end()

    def _named_image(self, name):
        self.set_name(name, 'NOTHING')
        self.take_image()

    def z_stack(self, range_pm, steps, base_name='', image_fun='default', return_fn=False):
        """
        Take a z-stack centered on the current position
        
        TODO: PFS???
        
        :param range_pm: will move from -range_pm to +range_pm
        :param steps: number of positions to take an image at
        :param base_name: this sets the base file name, only used if image_fun==default
        :param image_fun: function is called at every point z-position, receives name suffix,
                          for default see _named_image
        """
        #move to the start position
        def _zs(pref=""):
            self.move_z(-range_pm, 1)
            pos=-range_pm
            dz=2*range_pm/(steps-1)
            for i in range(steps):
                if image_fun == "default":
                    self._named_image(f"{base_name}{pref}_{pos}")
                else:
                    image_fun(f"{pref}_{pos}")
                pos+=dz
                self.move_z(dz,1)
            self.move_z(-range_pm,1) #return
        
        if return_fn:
            return _zs
        _zs()
    
    def rgb_image(self, prefix_name, led_intensities, return_fn=False):
        """
            Take images in RGB, with defined brightness. Can return function
            taking name suffix for use in functions such as z_stack.
            
            TODO: different camera settings for different leds
            
            :param led_intensities: rgb led intensities (in RGB order)
        """
        def _img(name_suffix):
            if name_suffix != "":
                ns=f"_{name_suffix}"
            else:
                ns=""
            #LED colours: R-2, G-1, B-0
            self.set_led(0,2,led_intensities[0])
            self.set_name(f"{prefix_name}{ns}_R","NOTHING")
            self.take_image()
            self.set_led(0,1,led_intensities[1])
            self.set_name(f"{prefix_name}{ns}_G","NOTHING")
            self.take_image()
            self.set_led(0,0,led_intensities[2])
            self.set_name(f"{prefix_name}{ns}_B","NOTHING")
            self.take_image()
            self.set_led(0,0,0)

        if return_fn:
            return _img
        _img("")

    def image_grid(self, step_sizes, steps, image_fn,
                   tilt=np.array([0,0])):
        """
            Take images in a grid starting at current position and moving
            to [+step_sizes[0]*(steps[0]-1),+step_sizes[1]*(steps[1]-1)],
            running image_fn at every position giving it relative x_y position.
            
            :param step_sizes: [dx, dy]
            :param steps: [steps_x, steps_y]
            :param image_fn: image function taking x_y position called at every point
            :param tilt: compensation for stage tilt, numpy array giving the rate with x,y
            :param return_fn: if this is true, will return a function accepting a name prefix
        """
        j=0
        direction=1
        #tiltmat=np.array([[1,0,0],[0,1,0],[tilt[0],tilt[1],1]])
        ystep=np.array([0,
                        step_sizes[1],
                        np.dot(tilt, np.array([0, step_sizes[1]]))
                          ])
        for i in range(steps[0]):
            y=i*step_sizes[1]
            step=np.array([direction*step_sizes[0],
                           0,
                           np.dot(tilt, np.array([direction*step_sizes[0],0]))
                          ])
            for j in range(steps[1]-1):
                x=j*step_sizes[0] if direction==1 else (steps[0]-1-j)*step_sizes[0]
                image_fn(f"x{x:3f}_x{x:3f}")
                self.move_relative(step,3) #TODO period???
                self.wait_for_move('x')
            x=(steps[0]-1)*step_sizes[0] if direction==1 else 0
            image_fn(f"x{x:3f}_y{y:3f}")
            self.move_relative(ystep,3)
            self.wait_for_move('y')
            direction*=-1