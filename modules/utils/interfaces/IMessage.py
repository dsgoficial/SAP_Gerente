class IMessage:
    
    def show(self, *args):
        raise NotImplementedError('Abstract Method')